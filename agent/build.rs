use pipl::*;
use std::process::Command;

fn emit_identity() {
    let output = Command::new("python3")
        .arg("../tools/agent_build_identity.py")
        .output()
        .expect("python3 is required for Agent build identity");
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    print!(
        "{}",
        String::from_utf8(output.stdout).expect("UTF-8 metadata")
    );
}

fn build_native_helpers() {
    #[cfg(target_os = "macos")]
    {
        cc::Build::new()
            .cpp(true)
            .file("native/ShellReloader.cpp")
            .flag("-std=c++17")
            .flag("-Wall")
            .flag("-Wextra")
            .flag("-Wpedantic")
            .flag("-Werror")
            .compile("ae_hot_loader_shell_reloader");

        cc::Build::new()
            .cpp(true)
            .file("native/InternalLoader.cpp")
            .file("native/AgentIdentity.cpp")
            .flag("-std=c++17")
            .flag("-Wall")
            .flag("-Wextra")
            .flag("-Wpedantic")
            .flag("-Werror")
            .compile("ae_hot_loader_internal_loader");

        println!("cargo:rustc-link-lib=c++");
        println!("cargo:rustc-link-lib=framework=CoreFoundation");
    }
}

#[rustfmt::skip]
fn main() {
    emit_identity();
    build_native_helpers();

    pipl::plugin_build(vec![
        Property::Kind(PIPLType::AEGP),
        Property::Name("AE Hot Loader Agent"),
        Property::Category("General Plugin"),
        #[cfg(target_os = "macos")]
        Property::CodeMacARM64("EntryPointFunc"),
    ]);
}
