use after_effects as ae;
use std::ffi::c_void;
use std::fs;
use std::path::PathBuf;
use std::sync::{
    atomic::{AtomicPtr, Ordering},
    OnceLock,
};

#[derive(Eq, PartialEq, Hash, Clone, Copy, Debug)]
enum Params {}

#[derive(Default)]
struct Plugin;

ae::define_effect!(Plugin, (), Params);

type RegisterLateFn = unsafe extern "C" fn() -> i32;

static REGISTER_LATE_FN: AtomicPtr<c_void> = AtomicPtr::new(std::ptr::null_mut());
static PLUGIN_ID: OnceLock<i32> = OnceLock::new();

#[unsafe(no_mangle)]
pub extern "C" fn AEHotLoaderCore_SetRegisterFn(ptr: *mut c_void) {
    REGISTER_LATE_FN.store(ptr, Ordering::Release);
}

fn register_late_effect() -> i32 {
    let ptr = REGISTER_LATE_FN.load(Ordering::Acquire);
    if ptr.is_null() {
        return -1001;
    }

    let callback: RegisterLateFn = unsafe { std::mem::transmute(ptr) };
    unsafe { callback() }
}

fn bridge_dir() -> Option<PathBuf> {
    let home = std::env::var_os("HOME")?;
    Some(
        PathBuf::from(home)
            .join("Library")
            .join("Application Support")
            .join("AE Hot Loader")
            .join("bridge"),
    )
}

fn parse_value(text: &str, key: &str) -> Option<String> {
    text.lines().find_map(|line| {
        let (k, v) = line.split_once('=')?;
        if k == key {
            Some(v.to_string())
        } else {
            None
        }
    })
}

fn sanitize_message(message: &str) -> String {
    message
        .replace('\r', " ")
        .replace('\n', " ")
        .replace('=', ":")
}

fn write_response(request_id: &str, status: &str, message: &str) {
    let Some(dir) = bridge_dir() else {
        return;
    };

    if fs::create_dir_all(&dir).is_err() {
        return;
    }

    let body = format!(
        "version=1\nrequest_id={}\nstatus={}\nmessage={}\n",
        request_id,
        status,
        sanitize_message(message)
    );

    let response_path = dir.join("response.txt");
    let temp_path = dir.join("response.tmp");
    if fs::write(&temp_path, body).is_ok() {
        let _ = fs::remove_file(&response_path);
        let _ = fs::rename(temp_path, response_path);
    }
}

fn process_bridge_request() {
    let Some(dir) = bridge_dir() else {
        return;
    };

    let request_path = dir.join("request.txt");
    if !request_path.exists() {
        return;
    }

    let text = match fs::read_to_string(&request_path) {
        Ok(text) => text,
        Err(_) => return,
    };

    // ScriptUI writes through a temp file, but keep the native side tolerant
    // of a partially visible request as well.
    if !text.ends_with('\n') {
        return;
    }

    let version = parse_value(&text, "version").unwrap_or_default();
    let request_id = match parse_value(&text, "request_id") {
        Some(id) if !id.is_empty() => id,
        _ => return,
    };
    let command = match parse_value(&text, "command") {
        Some(command) if !command.is_empty() => command,
        _ => return,
    };

    let _ = fs::remove_file(&request_path);

    if version != "1" {
        write_response(&request_id, "error", "Unsupported bridge protocol version");
        return;
    }

    if command != "reload_plugins" {
        write_response(&request_id, "error", "Unknown bridge command");
        return;
    }

    match register_late_effect() {
        0 => write_response(
            &request_id,
            "success",
            "Registration callback returned success. Check Effect > AE Hot Loader.",
        ),
        1 => write_response(
            &request_id,
            "noop",
            "Late test effect is already registered in this AE process.",
        ),
        rc => write_response(
            &request_id,
            "error",
            &format!("Registration callback failed with code {rc}"),
        ),
    }
}

impl AdobePluginGlobal for Plugin {
    fn params_setup(
        &self,
        _: &mut ae::Parameters<Params>,
        _: ae::InData,
        _: ae::OutData,
    ) -> Result<(), Error> {
        Ok(())
    }

    fn handle_command(
        &mut self,
        cmd: ae::Command,
        _: ae::InData,
        mut out_data: ae::OutData,
        _: &mut ae::Parameters<Params>,
    ) -> Result<(), ae::Error> {
        match cmd {
            ae::Command::GlobalSetup => {
                if PLUGIN_ID.get().is_none() {
                    let utility = ae::aegp::suites::Utility::new()?;
                    let plugin_id = utility.register_with_aegp("AEHotLoaderBridge")?;
                    let _ = PLUGIN_ID.set(plugin_id);

                    let register = ae::aegp::suites::RegisterNonAegp::new()?;
                    register
                        .register_idle_hook(
                            plugin_id,
                            Box::new(|_, _min_time| {
                                process_bridge_request();
                                Ok(())
                            }),
                            (),
                        )?;
                }
            }
            ae::Command::About => {
                out_data.set_return_msg(
                    "AE Hot Loader bridge\rBackground helper for the dockable ScriptUI panel.",
                );
            }
            ae::Command::Render {
                in_layer,
                mut out_layer,
            } => {
                out_layer.copy_from(&in_layer, None, None)?;
            }
            _ => {}
        }

        Ok(())
    }
}
