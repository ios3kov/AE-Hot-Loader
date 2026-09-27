use pipl::*;

const PF_PLUG_IN_VERSION: u16 = 13;
const PF_PLUG_IN_SUBVERS: u16 = 29;

fn main() {
    pipl::plugin_build(vec![
        Property::Kind(PIPLType::AEEffect),
        Property::Name("AE Hot Loader Rust Probe Permissive"),
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
        Property::AE_Effect_Global_OutFlags(OutFlags::PixIndependent),
        Property::AE_Effect_Global_OutFlags_2(OutFlags2::empty()),
        Property::AE_Effect_Match_Name("OS3KOV.AEHotLoader.RustProbe.Permissive"),
        Property::AE_Reserved_Info(0),
        Property::AE_Effect_Support_URL("https://github.com/ios3kov/AE-Hot-Loader"),
    ]);
}
