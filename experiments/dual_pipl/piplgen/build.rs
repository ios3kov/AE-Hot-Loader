use pipl::*;

const PF_PLUG_IN_VERSION: u16 = 13;
const PF_PLUG_IN_SUBVERS: u16 = 29;

fn effect_props(name: &'static str, match_name: &'static str) -> Vec<Property> {
    vec![
        Property::Kind(PIPLType::AEEffect),
        Property::Name(name),
        Property::Category("AE Hot Loader Diagnostic"),
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
        Property::AE_Effect_Match_Name(match_name),
        Property::AE_Reserved_Info(0),
        Property::AE_Effect_Support_URL("https://github.com/ios3kov/AE-Hot-Loader"),
    ]
}

fn main() {
    let pipl_a = build_pipl(effect_props(
        "AE Hot Loader Dual PiPL Fresh A",
        "OS3KOV.AEHotLoader.DualPiPL.Fresh.A",
    ))
    .expect("build PiPL A");

    let pipl_b = build_pipl(effect_props(
        "AE Hot Loader Dual PiPL Fresh B",
        "OS3KOV.AEHotLoader.DualPiPL.Fresh.B",
    ))
    .expect("build PiPL B");

    let resources = [
        (16000_i16, pipl_a.as_slice()),
        (16001_i16, pipl_b.as_slice()),
    ];

    let rsrc = create_rsrc(&[(b"PiPL", &resources)]).expect("create dual PiPL rsrc");

    let out = std::path::Path::new(&std::env::var("CARGO_MANIFEST_DIR").unwrap())
        .parent()
        .unwrap()
        .join("DualPiPL.rsrc");

    std::fs::write(out, rsrc).expect("write dual PiPL resource");
}
