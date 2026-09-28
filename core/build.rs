use pipl::*;
use std::process::Command;

const PF_PLUG_IN_VERSION: u16 = 13;
const PF_PLUG_IN_SUBVERS: u16 = 29;

fn main() {
    let rustc = std::env::var("RUSTC").unwrap_or_else(|_| "rustc".to_string());
    let rustc_version = Command::new(rustc)
        .arg("--version")
        .output()
        .ok()
        .and_then(|out| String::from_utf8(out.stdout).ok())
        .map(|s| s.trim().to_string())
        .unwrap_or_else(|| "rustc-unknown".to_string());
    let target = std::env::var("TARGET").unwrap_or_else(|_| "target-unknown".to_string());
    println!(
        "cargo:rustc-env=AE_HOT_LOADER_RUNTIME_ABI={}|{}|after-effects=83dcc93734fd5db1335b6ec83cba7a6505a39dcc",
        rustc_version, target
    );
    for name in [
        "catch_panics",
        "threaded_rendering",
        "smart_render",
        "gpu_render",
        "does_dialog",
        "uses_audio",
        "sends_update_params_ui",
        "with_premiere",
    ] {
        println!("cargo:rustc-check-cfg=cfg({name})");
    }
    println!("cargo:rustc-cfg=catch_panics");

    pipl::plugin_build(vec![
        Property::Kind(PIPLType::AEEffect),
        Property::Name("AE Hot Loader Control Shell"),
        Property::Category("AE Hot Loader"),
        #[cfg(target_os = "macos")]
        Property::CodeMacARM64("EffectMain"),
        Property::AE_PiPL_Version { major: 2, minor: 0 },
        Property::AE_Effect_Spec_Version {
            major: PF_PLUG_IN_VERSION,
            minor: PF_PLUG_IN_SUBVERS,
        },
        Property::AE_Effect_Version {
            version: 0,
            subversion: 1,
            bugversion: 0,
            stage: Stage::Develop,
            build: 1,
        },
        Property::AE_Effect_Info_Flags(0),
        Property::AE_Effect_Global_OutFlags(OutFlags::PixIndependent | OutFlags::DeepColorAware),
        Property::AE_Effect_Global_OutFlags_2(OutFlags2::empty()),
        Property::AE_Effect_Match_Name("OS3KOV.AEHotLoader.ControlShell"),
        Property::AE_Reserved_Info(0),
        Property::AE_Effect_Support_URL("https://github.com/ios3kov/AE-Hot-Loader"),
    ]);
}
