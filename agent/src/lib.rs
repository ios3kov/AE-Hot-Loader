use after_effects as ae;
use std::collections::{BTreeMap, BTreeSet};
use std::ffi::CString;
use std::fs;
use std::io::Write;
use std::os::raw::{c_char, c_int};
use std::path::{Path, PathBuf};
use std::sync::{Mutex, OnceLock};
use std::time::{SystemTime, UNIX_EPOCH};

use ae::{
    AegpPlugin, Error,
    aegp::{
        InstalledEffectKey,
        suites::{Effect as EffectSuite, Register},
    },
    define_general_plugin,
    pf::suites::{AdvApp, AdvItem},
    sys::AEGP_PluginID,
};

define_general_plugin!(Agent);

#[derive(Clone, Debug)]
struct Agent;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct Fingerprint {
    modified_ns: u128,
    bytes: u64,
}

static PLUGIN_SNAPSHOT: OnceLock<Mutex<BTreeMap<PathBuf, Fingerprint>>> = OnceLock::new();
static LAST_DIAG_GENERATION: OnceLock<Mutex<u64>> = OnceLock::new();

#[cfg(target_os = "macos")]
unsafe extern "C" {
    fn AEHotLoader_QueuePluginFolder(utf8_folder: *const c_char) -> c_int;
    fn AEHotLoader_GetLoadGeneration() -> u64;
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

fn plugin_roots() -> Vec<PathBuf> {
    let mut roots = Vec::new();

    roots.push(PathBuf::from(
        "/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore",
    ));
    roots.push(PathBuf::from(
        "/Library/Application Support/Adobe/Plug-Ins/CC",
    ));

    if let Some(home) = std::env::var_os("HOME") {
        let home = PathBuf::from(home);
        roots.push(
            home.join("Library")
                .join("Application Support")
                .join("Adobe")
                .join("Common")
                .join("Plug-ins")
                .join("7.0")
                .join("MediaCore"),
        );
        roots.push(
            home.join("Library")
                .join("Application Support")
                .join("Adobe")
                .join("Plug-Ins")
                .join("CC"),
        );
    }

    if let Ok(exe) = std::env::current_exe() {
        if let Some(app_bundle) = exe
            .ancestors()
            .find(|path| path.extension().is_some_and(|ext| ext == "app"))
        {
            if let Some(product_dir) = app_bundle.parent() {
                roots.push(product_dir.join("Plug-Ins"));
            }
        }
    }

    roots.sort();
    roots.dedup();
    roots
}

fn modified_ns(time: SystemTime) -> u128 {
    time.duration_since(UNIX_EPOCH)
        .map(|duration| duration.as_nanos())
        .unwrap_or(0)
}

fn update_fingerprint(path: &Path, fingerprint: &mut Fingerprint) {
    let Ok(metadata) = fs::metadata(path) else {
        return;
    };

    if let Ok(modified) = metadata.modified() {
        fingerprint.modified_ns = fingerprint.modified_ns.max(modified_ns(modified));
    }
    fingerprint.bytes = fingerprint.bytes.saturating_add(metadata.len());
}

fn bundle_fingerprint(bundle: &Path) -> Fingerprint {
    let mut fingerprint = Fingerprint {
        modified_ns: 0,
        bytes: 0,
    };

    update_fingerprint(bundle, &mut fingerprint);
    update_fingerprint(
        &bundle.join("Contents").join("Info.plist"),
        &mut fingerprint,
    );

    let macos = bundle.join("Contents").join("MacOS");
    update_fingerprint(&macos, &mut fingerprint);

    if let Ok(entries) = fs::read_dir(macos) {
        for entry in entries.flatten() {
            update_fingerprint(&entry.path(), &mut fingerprint);
        }
    }

    fingerprint
}

fn scan_root(root: &Path, depth: usize, out: &mut BTreeMap<PathBuf, Fingerprint>) {
    if depth > 10 {
        return;
    }

    let Ok(entries) = fs::read_dir(root) else {
        return;
    };

    for entry in entries.flatten() {
        let path = entry.path();
        let Ok(file_type) = entry.file_type() else {
            continue;
        };

        if file_type.is_symlink() || !file_type.is_dir() {
            continue;
        }

        if path.extension().is_some_and(|ext| ext == "plugin") {
            out.insert(path.clone(), bundle_fingerprint(&path));
            continue;
        }

        scan_root(&path, depth + 1, out);
    }
}

fn scan_plugins() -> BTreeMap<PathBuf, Fingerprint> {
    let mut found = BTreeMap::new();

    for root in plugin_roots() {
        scan_root(&root, 0, &mut found);
    }

    found
}

fn initialize_snapshot() {
    let snapshot = scan_plugins();
    let count = snapshot.len();
    let _ = PLUGIN_SNAPSHOT.set(Mutex::new(snapshot));
    log_line(&format!(
        "plugin snapshot initialized with {count} bundle(s)"
    ));
}

#[cfg(target_os = "macos")]
fn queue_folder(folder: &Path) -> i32 {
    let path = folder.to_string_lossy();
    let Ok(c_path) = CString::new(path.as_bytes()) else {
        return -3101;
    };

    unsafe { AEHotLoader_QueuePluginFolder(c_path.as_ptr()) }
}

#[cfg(not(target_os = "macos"))]
fn queue_folder(_folder: &Path) -> i32 {
    -3199
}

#[cfg(target_os = "macos")]
fn diagnose_effect_registry_if_needed() {
    let generation = unsafe { AEHotLoader_GetLoadGeneration() };
    if generation == 0 {
        return;
    }

    let last = LAST_DIAG_GENERATION.get_or_init(|| Mutex::new(0));
    let mut last = match last.lock() {
        Ok(last) => last,
        Err(_) => return,
    };
    if *last == generation {
        return;
    }

    let suite = match EffectSuite::new() {
        Ok(suite) => suite,
        Err(error) => {
            log_line(&format!(
                "registry-diag: EffectSuite unavailable: {error:?}"
            ));
            *last = generation;
            return;
        }
    };

    let count = match suite.num_installed_effects() {
        Ok(count) => count,
        Err(error) => {
            log_line(&format!("registry-diag: count failed: {error:?}"));
            *last = generation;
            return;
        }
    };

    log_line(&format!(
        "registry-diag: generation={generation} installed_effects={count}"
    ));

    let mut key = InstalledEffectKey::None;
    let mut found = 0usize;

    for _ in 0..count.max(0) {
        key = match suite.next_installed_effect(key) {
            Ok(InstalledEffectKey::None) => break,
            Ok(key) => key,
            Err(error) => {
                log_line(&format!("registry-diag: next failed: {error:?}"));
                break;
            }
        };

        let name = suite.effect_name(key).unwrap_or_default();
        let match_name = suite.effect_match_name(key).unwrap_or_default();
        let category = suite.effect_category(key).unwrap_or_default();

        if name.contains("AE Hot Loader")
            || match_name.contains("AEHotLoader")
            || category.contains("AE Hot Loader")
        {
            found += 1;
            log_line(&format!(
                "registry-diag: FOUND key={key:?} name={name:?} match={match_name:?} category={category:?}"
            ));
        }
    }

    log_line(&format!(
        "registry-diag: generation={generation} matching_effects={found}"
    ));

    if found > 0 {
        match AdvItem::new().and_then(|suite| suite.touch_active_item()) {
            Ok(()) => log_line("ui-refresh: PF_TouchActiveItem ok"),
            Err(error) => log_line(&format!("ui-refresh: PF_TouchActiveItem failed: {error:?}")),
        }

        match AdvApp::new().and_then(|suite| suite.refresh_all_windows()) {
            Ok(()) => log_line("ui-refresh: PF_RefreshAllWindows ok"),
            Err(error) => log_line(&format!(
                "ui-refresh: PF_RefreshAllWindows failed: {error:?}"
            )),
        }
    }

    *last = generation;
}

#[cfg(not(target_os = "macos"))]
fn diagnose_effect_registry_if_needed() {}

enum ReloadResult {
    Success(String),
    Noop(String),
    Error(String),
}

fn reload_plugins() -> ReloadResult {
    let current = scan_plugins();
    let snapshot = PLUGIN_SNAPSHOT.get_or_init(|| Mutex::new(current.clone()));

    let mut previous = match snapshot.lock() {
        Ok(snapshot) => snapshot,
        Err(_) => {
            return ReloadResult::Error("Plugin snapshot lock failed.".to_string());
        }
    };

    let new_bundles: Vec<PathBuf> = current
        .keys()
        .filter(|path| !previous.contains_key(*path))
        .cloned()
        .collect();

    let changed_bundles: Vec<PathBuf> = current
        .iter()
        .filter_map(|(path, fingerprint)| match previous.get(path) {
            Some(previous_fingerprint) if previous_fingerprint != fingerprint => Some(path.clone()),
            _ => None,
        })
        .collect();

    if new_bundles.is_empty() && changed_bundles.is_empty() {
        return ReloadResult::Noop("No new or changed .plugin bundles found.".to_string());
    }

    for plugin in &new_bundles {
        log_line(&format!("reload: new bundle {}", plugin.display()));
    }
    for plugin in &changed_bundles {
        log_line(&format!(
            "reload: changed existing bundle {}",
            plugin.display()
        ));
    }

    let mut folders = BTreeSet::new();
    for plugin in &new_bundles {
        if let Some(parent) = plugin.parent() {
            folders.insert(parent.to_path_buf());
        }
    }

    let mut failures = Vec::new();

    for folder in &folders {
        log_line(&format!("reload: queueing {}", folder.display()));
        let result = queue_folder(folder);
        log_line(&format!(
            "reload: queue folder={} result={result}",
            folder.display()
        ));

        if result < 0 {
            failures.push(format!("{} ({result})", folder.display()));
        }
    }

    for plugin in new_bundles.iter().chain(changed_bundles.iter()) {
        if let Some(fingerprint) = current.get(plugin) {
            previous.insert(plugin.clone(), *fingerprint);
        }
    }

    if !failures.is_empty() {
        return ReloadResult::Error(format!("Internal loader failed: {}", failures.join(", ")));
    }

    if !new_bundles.is_empty() {
        let mut message = format!("Queued {} new bundle(s) for AE loader.", new_bundles.len());

        if !changed_bundles.is_empty() {
            message.push_str(&format!(
                " Also detected {} changed existing bundle(s); hot replacement is not verified.",
                changed_bundles.len()
            ));
        }

        ReloadResult::Success(message)
    } else {
        ReloadResult::Noop(format!(
            "Detected {} changed existing bundle(s). Hot replacement of already-loaded plug-ins is not verified; restart AE to guarantee update.",
            changed_bundles.len()
        ))
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

    match reload_plugins() {
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
            "agent start AE API {major_version}.{minor_version}, plugin_id={aegp_plugin_id}"
        ));

        initialize_snapshot();

        let register = Register::new()?;
        register.register_idle_hook::<Agent, _>(
            aegp_plugin_id,
            Box::new(|_, _, max_sleep| {
                process_request();
                diagnose_effect_registry_if_needed();
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
