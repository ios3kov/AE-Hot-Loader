use after_effects as ae;
use std::ffi::CStr;
use std::fs;
use std::io::Write;
use std::os::raw::{c_char, c_int};
use std::path::PathBuf;

use ae::{AegpPlugin, Error, aegp::suites::Register, define_general_plugin, sys::AEGP_PluginID};

define_general_plugin!(Agent);

const BUILD_ID: &str = "shell-reload-v1";

#[derive(Clone, Debug)]
struct Agent;

#[cfg(target_os = "macos")]
unsafe extern "C" {
    fn AEHotLoader_ReloadShells(output: *mut c_char, output_capacity: usize) -> c_int;
}

fn log_line(message: &str) {
    if let Ok(mut file) = fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open("/tmp/ae-hot-loader-agent.log")
    {
        let _ = writeln!(file, "{message}");
    }
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
        if k == key { Some(v.to_string()) } else { None }
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

    let response = dir.join("response.txt");
    let temp = dir.join("response.tmp");

    if fs::write(&temp, body).is_ok() {
        let _ = fs::remove_file(&response);
        let _ = fs::rename(temp, response);
    }
}

enum ReloadResult {
    Success(String),
    Noop(String),
    Error(String),
}

#[cfg(target_os = "macos")]
fn reload_shell_implementations() -> ReloadResult {
    let mut buffer = [0 as c_char; 2048];
    let result = unsafe { AEHotLoader_ReloadShells(buffer.as_mut_ptr(), buffer.len()) };

    let message = unsafe { CStr::from_ptr(buffer.as_ptr()) }
        .to_string_lossy()
        .into_owned();

    log_line(&format!(
        "shell-reload: result={result} message={message:?}"
    ));

    match result {
        0 => ReloadResult::Success(format!("{BUILD_ID}: {message}")),
        1 => ReloadResult::Noop(format!("{BUILD_ID}: {message}")),
        _ => ReloadResult::Error(format!("{BUILD_ID}: {message}")),
    }
}

#[cfg(not(target_os = "macos"))]
fn reload_shell_implementations() -> ReloadResult {
    ReloadResult::Error(format!("{BUILD_ID}: unsupported platform"))
}

fn process_request() {
    let Some(dir) = bridge_dir() else {
        return;
    };

    let request = dir.join("request.txt");
    if !request.exists() {
        return;
    }

    let text = match fs::read_to_string(&request) {
        Ok(text) => text,
        Err(error) => {
            log_line(&format!("request read failed: {error}"));
            return;
        }
    };

    if !text.ends_with('\n') {
        return;
    }

    let request_id = match parse_value(&text, "request_id") {
        Some(id) if !id.is_empty() => id,
        _ => return,
    };

    let version = parse_value(&text, "version").unwrap_or_default();
    let command = parse_value(&text, "command").unwrap_or_default();

    let _ = fs::remove_file(&request);

    if version != "1" {
        write_response(&request_id, "error", "Unsupported bridge protocol version");
        return;
    }

    if command != "reload_plugins" {
        write_response(&request_id, "error", "Unknown bridge command");
        return;
    }

    match reload_shell_implementations() {
        ReloadResult::Success(message) => write_response(&request_id, "success", &message),
        ReloadResult::Noop(message) => write_response(&request_id, "noop", &message),
        ReloadResult::Error(message) => write_response(&request_id, "error", &message),
    }
}

impl AegpPlugin for Agent {
    fn entry_point(
        major_version: i32,
        minor_version: i32,
        aegp_plugin_id: AEGP_PluginID,
    ) -> Result<Self, ae::Error> {
        log_line(&format!(
            "agent start build={BUILD_ID} AE API {major_version}.{minor_version}, plugin_id={aegp_plugin_id}"
        ));

        let register = Register::new()?;
        register.register_idle_hook::<Agent, _>(
            aegp_plugin_id,
            Box::new(|_, _, max_sleep| {
                process_request();
                if *max_sleep > 100 {
                    *max_sleep = 100;
                }
                Ok(())
            }),
            (),
        )?;

        log_line("idle hook registered; production path=shell reload");
        Ok(Agent)
    }
}
