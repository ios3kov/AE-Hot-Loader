use pipl::*;

fn build_internal_loader() {
    #[cfg(target_os = "macos")]
    {
        cc::Build::new()
            .cpp(true)
            .file("native/InternalLoader.cpp")
            .file("native/ShellReloader.cpp")
            .flag("-std=c++17")
            .flag("-Wall")
            .flag("-Wextra")
            .flag("-Wpedantic")
            .flag("-Werror")
            .compile("ae_hot_loader_internal");

        println!("cargo:rustc-link-lib=framework=CoreFoundation");
        println!("cargo:rustc-link-lib=c++");
    }
}

#[rustfmt::skip]
fn main() {
    build_internal_loader();

    pipl::plugin_build(vec![
        Property::Kind(PIPLType::AEGP),
        Property::Name("AE Hot Loader Agent"),
        Property::Category("General Plugin"),
        #[cfg(target_os = "macos")]
        Property::CodeMacARM64("EntryPointFunc"),
    ]);
}
