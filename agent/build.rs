use pipl::*;

fn build_shell_reloader() {
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

        println!("cargo:rustc-link-lib=c++");
    }
}

#[rustfmt::skip]
fn main() {
    build_shell_reloader();

    pipl::plugin_build(vec![
        Property::Kind(PIPLType::AEGP),
        Property::Name("AE Hot Loader Agent"),
        Property::Category("General Plugin"),
        #[cfg(target_os = "macos")]
        Property::CodeMacARM64("EntryPointFunc"),
    ]);
}
