use pipl::*;

fn main() {
    let pipl = build_pipl(vec![
        Property::Kind(PIPLType::AEEffect),
        Property::Name("AE Hot Loader Single PiPL C++"),
        Property::Category("AE Hot Loader Diagnostic"),
        Property::CodeMacARM64("EffectMain"),
        Property::AE_PiPL_Version { major: 2, minor: 0 },
        Property::AE_Effect_Spec_Version {
            major: 13,
            minor: 29,
        },
        Property::AE_Effect_Version {
            version: 0,
            subversion: 1,
            bugversion: 0,
            stage: Stage::Develop,
            build: 1,
        },
        Property::AE_Effect_Info_Flags(0),
        Property::AE_Effect_Global_OutFlags(OutFlags::PixIndependent),
        Property::AE_Effect_Global_OutFlags_2(OutFlags2::empty()),
        Property::AE_Effect_Match_Name("OS3KOV.AEHotLoader.SinglePiPLCpp"),
        Property::AE_Reserved_Info(0),
        Property::AE_Effect_Support_URL("https://github.com/ios3kov/AE-Hot-Loader"),
    ])
    .expect("build single PiPL");

    let resources = [(16000_i16, pipl.as_slice())];
    let rsrc = create_rsrc(&[(b"PiPL", &resources)]).expect("create rsrc");

    let out = std::path::Path::new(&std::env::var("CARGO_MANIFEST_DIR").unwrap())
        .parent()
        .unwrap()
        .join("SinglePiPLCpp.rsrc");
    std::fs::write(out, rsrc).expect("write rsrc");
}
