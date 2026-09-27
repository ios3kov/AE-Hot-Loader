use after_effects as ae;
use std::collections::BTreeMap;
use std::ffi::CString;
use std::fs;
use std::io::Write;
use std::os::raw::{c_char, c_int};
#[cfg(target_family = "unix")]
use std::os::unix::fs as unix_fs;
use std::path::{Path, PathBuf};
use std::sync::{Mutex, OnceLock};
use std::time::{SystemTime, UNIX_EPOCH};

use ae::{
    AegpPlugin, Error,
    aegp::{
        CommandHookStatus, HookPriority, InstalledEffectKey, MenuId, MenuOrder,
        suites::{Command, Effect as EffectSuite, Register},
    },
    define_general_plugin,
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
static LOADER_COMMAND: OnceLock<ae::sys::AEGP_Command> = OnceLock::new();
static PENDING_RUNTIME_ROOTS: OnceLock<Mutex<Vec<PathBuf>>> = OnceLock::new();
static LAST_COMMAND_RESULTS: OnceLock<Mutex<Vec<(PathBuf, i32)>>> = OnceLock::new();

#[cfg(target_os = "macos")]
unsafe extern "C" {
    fn AEHotLoader_LoadPluginFolder(utf8_folder: *const c_char) -> c_int;
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
fn load_folder_sync(folder: &Path) -> i32 {
    let path = folder.to_string_lossy();
    let Ok(c_path) = CString::new(path.as_bytes()) else {
        return -3101;
    };

    unsafe { AEHotLoader_LoadPluginFolder(c_path.as_ptr()) }
}

#[cfg(not(target_os = "macos"))]
fn load_folder_sync(_folder: &Path) -> i32 {
    -3199
}

#[derive(Clone, Debug)]
struct RegistryEffectInfo {
    name: String,
    match_name: String,
    category: String,
}

fn capture_effect_registry() -> Result<BTreeMap<String, RegistryEffectInfo>, String> {
    let suite =
        EffectSuite::new().map_err(|error| format!("EffectSuite unavailable: {error:?}"))?;
    let count = suite
        .num_installed_effects()
        .map_err(|error| format!("installed effect count failed: {error:?}"))?;

    let mut key = InstalledEffectKey::None;
    let mut effects = BTreeMap::new();

    for _ in 0..count.max(0) {
        key = match suite.next_installed_effect(key) {
            Ok(InstalledEffectKey::None) => break,
            Ok(key) => key,
            Err(error) => return Err(format!("next installed effect failed: {error:?}")),
        };

        let name = suite.effect_name(key).unwrap_or_default();
        let match_name = suite.effect_match_name(key).unwrap_or_default();
        let category = suite.effect_category(key).unwrap_or_default();

        let identity = format!("{match_name}\u{1f}{name}\u{1f}{category}");
        effects.insert(
            identity,
            RegistryEffectInfo {
                name,
                match_name,
                category,
            },
        );
    }

    Ok(effects)
}

fn find_registry_matches(
    snapshot: &BTreeMap<String, RegistryEffectInfo>,
    needles: &[&str],
) -> Vec<RegistryEffectInfo> {
    snapshot
        .values()
        .filter(|info| {
            needles.iter().any(|needle| {
                info.match_name.eq_ignore_ascii_case(needle)
                    || info.name.eq_ignore_ascii_case(needle)
            })
        })
        .cloned()
        .collect()
}

fn registry_diff(
    before: &BTreeMap<String, RegistryEffectInfo>,
    after: &BTreeMap<String, RegistryEffectInfo>,
) -> Vec<RegistryEffectInfo> {
    after
        .iter()
        .filter_map(|(identity, info)| {
            if before.contains_key(identity) {
                None
            } else {
                Some(info.clone())
            }
        })
        .collect()
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

    *last = generation;
}

#[cfg(not(target_os = "macos"))]
fn diagnose_effect_registry_if_needed() {}

fn copy_tree(source: &Path, destination: &Path) -> Result<(), String> {
    let metadata = fs::symlink_metadata(source)
        .map_err(|error| format!("metadata {}: {error}", source.display()))?;

    if metadata.file_type().is_symlink() {
        #[cfg(target_family = "unix")]
        {
            let target = fs::read_link(source)
                .map_err(|error| format!("readlink {}: {error}", source.display()))?;
            unix_fs::symlink(&target, destination)
                .map_err(|error| format!("symlink {}: {error}", destination.display()))?;
            return Ok(());
        }

        #[cfg(not(target_family = "unix"))]
        {
            return Err(format!("symlink staging unsupported: {}", source.display()));
        }
    }

    if metadata.is_dir() {
        fs::create_dir_all(destination)
            .map_err(|error| format!("mkdir {}: {error}", destination.display()))?;

        let entries = fs::read_dir(source)
            .map_err(|error| format!("readdir {}: {error}", source.display()))?;
        for entry in entries {
            let entry = entry.map_err(|error| format!("readdir entry: {error}"))?;
            copy_tree(&entry.path(), &destination.join(entry.file_name()))?;
        }
        return Ok(());
    }

    if metadata.is_file() {
        if let Some(parent) = destination.parent() {
            fs::create_dir_all(parent)
                .map_err(|error| format!("mkdir {}: {error}", parent.display()))?;
        }
        fs::copy(source, destination).map_err(|error| {
            format!(
                "copy {} -> {}: {error}",
                source.display(),
                destination.display()
            )
        })?;

        let permissions = metadata.permissions();
        let _ = fs::set_permissions(destination, permissions);
        return Ok(());
    }

    Err(format!("unsupported file type: {}", source.display()))
}

fn stage_bundle_for_runtime(bundle: &Path, ordinal: usize) -> Result<PathBuf, String> {
    let stamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|duration| duration.as_nanos())
        .unwrap_or(0);
    let pid = std::process::id();
    let root =
        PathBuf::from("/private/tmp/AEHotLoaderRuntime").join(format!("{pid}-{stamp}-{ordinal}"));

    fs::create_dir_all(&root)
        .map_err(|error| format!("create runtime root {}: {error}", root.display()))?;

    let name = bundle
        .file_name()
        .ok_or_else(|| format!("bundle has no file name: {}", bundle.display()))?;
    let staged_bundle = root.join(name);

    copy_tree(bundle, &staged_bundle)?;

    log_line(&format!(
        "reload: staged {} -> {}",
        bundle.display(),
        staged_bundle.display()
    ));

    Ok(root)
}

fn run_roots_via_ae_command(roots: Vec<PathBuf>) -> Result<Vec<(PathBuf, i32)>, String> {
    let command = *LOADER_COMMAND
        .get()
        .ok_or_else(|| "Loader command is not initialized.".to_string())?;

    let expected_count = roots.len();

    let pending = PENDING_RUNTIME_ROOTS.get_or_init(|| Mutex::new(Vec::new()));
    {
        let mut pending = pending
            .lock()
            .map_err(|_| "Pending runtime roots lock failed.".to_string())?;
        *pending = roots;
    }

    let results = LAST_COMMAND_RESULTS.get_or_init(|| Mutex::new(Vec::new()));
    {
        let mut results = results
            .lock()
            .map_err(|_| "Command results lock failed.".to_string())?;
        results.clear();
    }

    log_line(&format!(
        "reload: dispatching AEGP_DoCommand command={command}"
    ));

    Command::new()
        .and_then(|suite| suite.do_command(command))
        .map_err(|error| format!("AEGP_DoCommand failed: {error:?}"))?;

    let collected = results
        .lock()
        .map(|results| results.clone())
        .map_err(|_| "Command results lock failed after dispatch.".to_string())?;

    if collected.len() != expected_count {
        return Err(format!(
            "AEGP command hook did not execute completely: expected {expected_count} result(s), got {}.",
            collected.len()
        ));
    }

    Ok(collected)
}

enum ReloadResult {
    Success(String),
    Noop(String),
    Error(String),
}

fn reload_plugins() -> ReloadResult {
    let _ = fs::write(
        "/tmp/ae-hot-loader-diagnostic-report.log",
        "AE Hot Loader unified diagnostic report\n\n",
    );

    let registry_before = match capture_effect_registry() {
        Ok(snapshot) => snapshot,
        Err(error) => {
            return ReloadResult::Error(format!(
                "Could not snapshot AE effect registry before load: {error}"
            ));
        }
    };

    let known_matches = [
        "com.elasticgrid.fx.warp",
        "StellarLabs.StellarGradient",
        "ElasticGrid FX",
        "Stellar Gradient",
        "OS3KOV.AEHotLoader.RustProbe",
        "OS3KOV.AEHotLoader.RustProbe.Permissive",
        "AE Hot Loader Rust Probe",
        "AE Hot Loader Rust Probe Permissive",
    ];
    let preexisting_target_effects = find_registry_matches(&registry_before, &known_matches);
    for effect in &preexisting_target_effects {
        log_line(&format!(
            "registry-pre: TARGET already present name={:?} match={:?} category={:?}",
            effect.name, effect.match_name, effect.category
        ));
    }

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

    let mut runtime_roots = Vec::new();
    let mut staged_pairs: Vec<(PathBuf, PathBuf)> = Vec::new();
    let mut failures = Vec::new();

    for (ordinal, plugin) in new_bundles.iter().enumerate() {
        match stage_bundle_for_runtime(plugin, ordinal) {
            Ok(root) => {
                staged_pairs.push((plugin.clone(), root.clone()));
                runtime_roots.push(root);
            },
            Err(error) => failures.push(error),
        }
    }

    let mut loader_results = Vec::new();

    if failures.is_empty() && !runtime_roots.is_empty() {
        match run_roots_via_ae_command(runtime_roots.clone()) {
            Ok(results) => {
                for (root, result) in results {
                    log_line(&format!(
                        "reload: command root={} result={result}",
                        root.display()
                    ));
                    loader_results.push((root.clone(), result));
                    if result <= 0 {
                        failures.push(format!("{} ({result})", root.display()));
                    }
                }
            }
            Err(error) => failures.push(error),
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
        let registry_after = match capture_effect_registry() {
            Ok(snapshot) => snapshot,
            Err(error) => {
                return ReloadResult::Error(format!(
                    "Loader executed, but AE effect registry snapshot after load failed: {error}"
                ));
            }
        };

        let added_effects = registry_diff(&registry_before, &registry_after);

        log_line(&format!(
            "registry-diff: before={} after={} added={}",
            registry_before.len(),
            registry_after.len(),
            added_effects.len()
        ));

        for effect in &added_effects {
            log_line(&format!(
                "registry-diff: ADDED name={:?} match={:?} category={:?}",
                effect.name, effect.match_name, effect.category
            ));
        }

        let permissive_trace = fs::read_to_string(
            "/tmp/ae-hot-loader-rust-probe-permissive.log",
        )
        .unwrap_or_else(|_| "(no permissive entrypoint trace)".to_string());

        let mut report = String::new();
        report.push_str(&format!(
            "registry_before={} registry_after={} added={}\n",
            registry_before.len(),
            registry_after.len(),
            added_effects.len()
        ));
        report.push_str("\nBundles:\n");

        for (index, (source, root)) in staged_pairs.iter().enumerate() {
            let result = loader_results
                .iter()
                .find(|(loaded_root, _)| loaded_root == root)
                .map(|(_, result)| *result)
                .unwrap_or(-9999);
            report.push_str(&format!(
                "{}. source={} runtime_root={} ML::LoadPlugins={}\n",
                index + 1,
                source.display(),
                root.display(),
                result
            ));
        }

        report.push_str("\nPreexisting target effects:\n");
        if preexisting_target_effects.is_empty() {
            report.push_str("(none)\n");
        } else {
            for effect in &preexisting_target_effects {
                report.push_str(&format!(
                    "name={:?} match={:?} category={:?}\n",
                    effect.name, effect.match_name, effect.category
                ));
            }
        }

        report.push_str("\nAdded effects:\n");
        if added_effects.is_empty() {
            report.push_str("(none)\n");
        } else {
            for effect in &added_effects {
                report.push_str(&format!(
                    "name={:?} match={:?} category={:?}\n",
                    effect.name, effect.match_name, effect.category
                ));
            }
        }

        report.push_str("\nPermissive PluginDataEntryFunction2 trace:\n");
        report.push_str(&permissive_trace);
        if !report.ends_with('\n') {
            report.push('\n');
        }

        if let Ok(mut file) = fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open("/tmp/ae-hot-loader-diagnostic-report.log")
        {
            let _ = file.write_all(report.as_bytes());
        }
        log_line("diagnostic-report: /tmp/ae-hot-loader-diagnostic-report.log");

        let loader_codes = loader_results
            .iter()
            .map(|(_, result)| result.to_string())
            .collect::<Vec<_>>()
            .join(",");

        let mut message = format!(
            "{} bundles: ML::LoadPlugins=[{loader_codes}], registry +{}; report: /tmp/ae-hot-loader-diagnostic-report.log",
            new_bundles.len(),
            added_effects.len()
        );

        if !preexisting_target_effects.is_empty() {
            let existing = preexisting_target_effects
                .iter()
                .map(|effect| format!("{} [{}]", effect.name, effect.match_name))
                .collect::<Vec<_>>()
                .join(", ");
            message.push_str(&format!("; target already in registry: {existing}"));
        }

        if !added_effects.is_empty() {
            let names = added_effects
                .iter()
                .take(4)
                .map(|effect| effect.name.as_str())
                .collect::<Vec<_>>()
                .join(", ");
            message.push_str(&format!(": {names}"));
            if added_effects.len() > 4 {
                message.push_str(", ...");
            }
        } else {
            message.push_str(".");
        }

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

        let command_suite = Command::new()?;
        let loader_command = command_suite.unique_command()?;
        command_suite.insert_command(
            "AE Hot Loader Internal",
            loader_command,
            MenuId::None,
            MenuOrder::Bottom,
        )?;
        let _ = LOADER_COMMAND.set(loader_command);

        let register = Register::new()?;
        register.register_command_hook::<Agent, _>(
            aegp_plugin_id,
            HookPriority::BeforeAE,
            loader_command,
            Box::new(move |_, _, command, _, _| {
                log_line(&format!(
                    "command-hook: begin command={command} main_thread_dispatch"
                ));

                let pending = PENDING_RUNTIME_ROOTS.get_or_init(|| Mutex::new(Vec::new()));
                let roots = match pending.lock() {
                    Ok(mut pending) => std::mem::take(&mut *pending),
                    Err(_) => {
                        log_line("command-hook: pending roots lock failed");
                        return Ok(CommandHookStatus::Handled);
                    }
                };

                let mut command_results = Vec::new();
                for root in roots {
                    let result = load_folder_sync(&root);
                    log_line(&format!(
                        "command-hook: load root={} result={result}",
                        root.display()
                    ));
                    command_results.push((root, result));
                }

                if let Ok(mut results) = LAST_COMMAND_RESULTS
                    .get_or_init(|| Mutex::new(Vec::new()))
                    .lock()
                {
                    *results = command_results;
                }

                log_line("command-hook: end");
                Ok(CommandHookStatus::Handled)
            }),
            (),
        )?;

        log_line(&format!(
            "loader command hook registered command={loader_command}"
        ));

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
