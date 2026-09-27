use pipl::*;

#[rustfmt::skip]
fn main() {
    pipl::plugin_build(vec![
        Property::Kind(PIPLType::AEGP),
        Property::Name("AE Hot Loader Agent"),
        Property::Category("General Plugin"),
        #[cfg(target_os = "macos")]
        Property::CodeMacARM64("EntryPointFunc"),
    ]);
}
