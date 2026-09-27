use after_effects as ae;
use libloading::Library;
use std::ffi::CStr;
use std::fs;
use std::io::Write;
use std::os::raw::c_char;
use std::path::PathBuf;

use ae::{AegpPlugin, Error, aegp::suites::Register, define_general_plugin, sys::AEGP_PluginID};

define_general_plugin!(Agent);

#[derive(Clone, Debug)]
struct Agent;

type RegisterLateFn = unsafe extern "C" fn() -> i32;

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

use after_effects as ae;
use libloading::Library;
use std::ffi::CStr;
use std::fs;
use std::io::Write;
use std::os::raw::c_char;
use std::path::PathBuf;

use ae::{AegpPlugin, Error, aegp::suites::Register, define_general_plugin, sys::AEGP_PluginID};

define_general_plugin!(Agent);

#[derive(Clone, Debug)]
struct Agent;

type RegisterLateFn = unsafe extern "C" fn() -> i32;

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

fn bridge_binary() -> Option<PathBuf> {
    let home = std::env::var_os("HOME")?;
    Some(
        PathBuf::from(home)
            .join("Library")
            .join("Application Support")
            .join("Adobe")
            .join("Common")
            .join("Plug-ins")
            .join("7.0")
            .join("MediaCore")
            .join("AEHotLoaderBridge.plugin")
            .join("Contents")
            .join("MacOS")
            .join("AEHotLoaderBridge"),
    )
}

#[cfg(target_os = "macos")]
unsafe extern "C" {
    fn _dyld_image_count() -> u32;
    fn _dyld_get_image_name(image_index: u32) -> *const c_char;
}

#[cfg(target_os = "macos")]
fn loaded_bridge_path() -> Option<PathBuf> {
    unsafe {
        let count = _dyld_image_count();
        for index in 0..count {
            let ptr = _dyld_get_image_name(index);
            if ptr.is_null() {
                continue;
            }

            let path = CStr::from_ptr(ptr).to_string_lossy();
            if path.contains("/AEHotLoaderBridge.plugin/Contents/MacOS/AEHotLoaderBridge") {
                return Some(PathBuf::from(path.as_ref()));
            }
        }
    }

    None
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

fn call_effect_bridge() -> i32 {
    unsafe {
        let process = libloading::os::unix::Library::this();
        match process.get::<RegisterLateFn>(b"AEHotLoader_RegisterLateEffect\0") {
            Ok(register) => {
                let result = register();
                log_line(&format!("bridge resolved from process, returned {result}"));
                return result;
            }
            Err(error) => {
                log_line(&format!("process dlsym miss: {error}"));
            }
        }
    }

    #[cfg(target_os = "macos")]
    {
        let Some(path) = loaded_bridge_path() else {
            log_line("bridge image is not loaded in After Effects");
            return -2005;
        };

        log_line(&format!("bridge image found: {}", path.display()));

        unsafe {
            let library = match Library::new(&path) {
                Ok(library) => library,
                Err(error) => {
                    log_line(&format!("bridge dlopen failed: {error}"));
                    return -2003;
                }
            };

            let register = match library.get::<RegisterLateFn>(b"AEHotLoader_RegisterLateEffect\0")
            {
                Ok(symbol) => symbol,
                Err(error) => {
                    log_line(&format!("bridge dlsym failed: {error}"));
                    return -2004;
                }
            };

            let result = register();
            log_line(&format!("bridge returned {result}"));
            return result;
        }
    }

    #[allow(unreachable_code)]
    -2006
}
use after_effects as ae;
use libloading::Library;
use std::ffi::CStr;
use std::fs;
use std::io::Write;
use std::os::raw::c_char;
use std::path::PathBuf;

use ae::{AegpPlugin, Error, aegp::suites::Register, define_general_plugin, sys::AEGP_PluginID};

define_general_plugin!(Agent);

#[derive(Clone, Debug)]
struct Agent;

type RegisterLateFn = unsafe extern "C" fn() -> i32;

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

use after_effects as ae;
use libloading::Library;
use std::ffi::CStr;
use std::fs;
use std::io::Write;
use std::os::raw::c_char;
use std::path::PathBuf;

use ae::{AegpPlugin, Error, aegp::suites::Register, define_general_plugin, sys::AEGP_PluginID};

define_general_plugin!(Agent);

#[derive(Clone, Debug)]
struct Agent;

type RegisterLateFn = unsafe extern "C" fn() -> i32;

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

fn bridge_binary() -> Option<PathBuf> {
    let home = std::env::var_os("HOME")?;
    Some(
        PathBuf::from(home)
            .join("Library")
            .join("Application Support")
            .join("Adobe")
            .join("Common")
            .join("Plug-ins")
            .join("7.0")
            .join("MediaCore")
            .join("AEHotLoaderBridge.plugin")
            .join("Contents")
            .join("MacOS")
            .join("AEHotLoaderBridge"),
    )
}

#[cfg(target_os = "macos")]
unsafe extern "C" {
    fn _dyld_image_count() -> u32;
    fn _dyld_get_image_name(image_index: u32) -> *const c_char;
}

#[cfg(target_os = "macos")]
fn loaded_bridge_path() -> Option<PathBuf> {
    unsafe {
        let count = _dyld_image_count();
        for index in 0..count {
            let ptr = _dyld_get_image_name(index);
            if ptr.is_null() {
                continue;
            }

            let path = CStr::from_ptr(ptr).to_string_lossy();
            if path.contains("/AEHotLoaderBridge.plugin/Contents/MacOS/AEHotLoaderBridge") {
                return Some(PathBuf::from(path.as_ref()));
            }
        }
    }

    None
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

fn call_effect_bridge() -> i32 {
    let Some(path) = bridge_binary() else {
        return -2001;
    };

    if !path.exists() {
        log_line(&format!("bridge binary missing: {}", path.display()));
        return -2002;
    }

    unsafe {
        let library = match Library::new(&path) {
            Ok(library) => library,
            Err(error) => {
                log_line(&format!("dlopen failed: {error}"));
                return -2003;
            }
        };

        let register: Symbol<RegisterLateFn> =
            match library.get(b"AEHotLoader_RegisterLateEffect\0") {
                Ok(symbol) => symbol,
                Err(error) => {
                    log_line(&format!("dlsym failed: {error}"));
                    return -2004;
                }
            };

        let result = register();
        log_line(&format!("bridge returned {result}"));
        result
    }
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

    match call_effect_bridge() {
        0 => write_response(
            &request_id,
            "success",
            "After Effects accepted late registration.",
        ),
        10001 => write_response(
            &request_id,
            "noop",
            "Late test effect is already registered.",
        ),
        1 => write_response(
            &request_id,
            "error",
            "After Effects rejected late registration (code 1).",
        ),
        -2005 => write_response(
            &request_id,
            "error",
            "Effect Bridge is not loaded inside After Effects.",
        ),
        code => write_response(
            &request_id,
            "error",
            &format!("Native bridge failed with code {code}."),
        ),
    }
}

impl AegpPlugin for Agent {
    fn entry_point(
        major_version: i32,
        minor_version: i32,
        aegp_plugin_id: AEGP_PluginID,
    ) -> Result<Self, ae::Error> {
        log_line(&format!(
            "agent start AE API {major_version}.{minor_version}, plugin_id={aegp_plugin_id}"
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

        log_line("idle hook registered");
        Ok(Agent)
    }
}
