use pipl::*;

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
    build_native_helpers();

    pipl::plugin_build(vec![
        Property::Kind(PIPLType::AEGP),
        Property::Name("AE Hot Loader Agent"),
        Property::Category("General Plugin"),
        #[cfg(target_os = "macos")]
        Property::CodeMacARM64("EntryPointFunc"),
    ]);
}
