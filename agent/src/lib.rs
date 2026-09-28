use after_effects as ae;
use std::fs;
use std::io::Write;
use std::os::raw::{c_char, c_int};
use std::path::PathBuf;

use ae::{AegpPlugin, Error, aegp::suites::Register, define_general_plugin, sys::AEGP_PluginID};

mod identity;

define_general_plugin!(Agent);

const BUILD_ID: &str = identity::BUILD_ID;
const LOADER_PATH_ID: &str = "ordinary-discovery-v1";

#[derive(Clone, Debug)]
struct Agent;

#[cfg(target_os = "macos")]
unsafe extern "C" {
    fn AEHotLoader_LoadPluginFolder(utf8_folder: *const c_char) -> c_int;
    fn AEHotLoader_GetLastAddedModuleCount() -> u64;
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
        "version=1\nrequest_id={}\nstatus={}\nmessage={}\nagent_build_id={}\nagent_git_commit={}\nagent_source_clean={}\nagent_target={}\nagent_version={}\n",
        request_id,
        status,
        sanitize_message(message),
        identity::BUILD_ID,
        identity::COMMIT,
        identity::SOURCE_CLEAN,
        identity::TARGET,
        identity::VERSION
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
fn ordinary_plugin_roots() -> Vec<PathBuf> {
    let mut roots = vec![
        PathBuf::from("/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore"),
        PathBuf::from("/Library/Application Support/Adobe/Plug-Ins/CC"),
    ];

    if let Some(home) = std::env::var_os("HOME") {
        let home = PathBuf::from(home);
        roots.push(home.join("Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore"));
        roots.push(home.join("Library/Application Support/Adobe/Plug-Ins/CC"));
    }

    if let Ok(entries) = fs::read_dir("/Applications") {
        for entry in entries.flatten() {
            let name = entry.file_name();
            if name.to_string_lossy().starts_with("Adobe After Effects") {
                roots.push(entry.path().join("Contents/Plug-ins"));
            }
        }
    }

    roots
}

#[cfg(target_os = "macos")]
fn discover_ordinary_plugins() -> ReloadResult {
    let mut scanned = 0;
    let mut loaded = 0;
    let mut added_modules = 0;
    let mut failures = Vec::new();

    for root in ordinary_plugin_roots() {
        if !root.is_dir() {
            continue;
        }
        scanned += 1;

        let root_text = root.to_string_lossy().into_owned();
        let root_c = match std::ffi::CString::new(root_text.as_bytes()) {
            Ok(value) => value,
            Err(_) => {
                failures.push(format!("{}: invalid path", root.display()));
                continue;
            }
        };

        let result = unsafe { AEHotLoader_LoadPluginFolder(root_c.as_ptr()) };
        if result >= 0 {
            loaded += result;
            added_modules += unsafe { AEHotLoader_GetLastAddedModuleCount() };
            log_line(&format!(
                "ordinary-discovery: root={} loaded={result}",
                root.display()
            ));
        } else {
            failures.push(format!("{}: error {result}", root.display()));
        }
    }

    let mut summary = format!(
        "{LOADER_PATH_ID}: build={BUILD_ID} scanned={scanned} loaded={loaded} post_load_modules={added_modules}"
    );
    if !failures.is_empty() {
        summary.push_str(&format!("; failures={}", failures.join(" | ")));
    }

    if !failures.is_empty() {
        ReloadResult::Error(summary)
    } else if loaded == 0 {
        ReloadResult::Noop(summary)
    } else {
        ReloadResult::Success(summary)
    }
}

#[cfg(not(target_os = "macos"))]
fn discover_ordinary_plugins() -> ReloadResult {
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

    if text.len() > 4096 || !text.ends_with('\n') {
        log_line("discarding malformed/incomplete bridge request");
        let _ = fs::remove_file(&request);
        return;
    }

    let request_id = match parse_value(&text, "request_id") {
        Some(id) if !id.is_empty() && id.len() <= 128 => id,
        _ => {
            log_line("discarding bridge request without a valid request_id");
            let _ = fs::remove_file(&request);
            return;
        }
    };

    let version = parse_value(&text, "version").unwrap_or_default();
    let command = parse_value(&text, "command").unwrap_or_default();

    let _ = fs::remove_file(&request);

    if version != "1" {
        write_response(&request_id, "error", "Unsupported bridge protocol version");
        return;
    }

    // Read-only diagnostics: intentionally before the native discovery path.
    if command == "get_build_identity" {
        write_response(&request_id, "success", identity::JSON);
        return;
    }

    if command != "reload_plugins" {
        write_response(&request_id, "error", "Unknown bridge command");
        return;
    }

    match discover_ordinary_plugins() {
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

        log_line(identity::JSON);

        let register = Register::new()?;
        register.register_idle_hook::<Agent, _>(
            aegp_plugin_id,
            Box::new(|_, _, max_sleep| {
                process_request();
                if *max_sleep > 250 {
                    *max_sleep = 250;
                }
                Ok(())
            }),
            (),
        )?;

        log_line("idle hook registered; production path=ordinary discovery");
        Ok(Agent)
    }
}
