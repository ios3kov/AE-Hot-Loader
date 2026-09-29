/* Offline control: SDK-defined properties, matching the diagnostic builder. */
#include "AE_General.r"
resource 'PiPL' (16000) {
    {
        Kind { AEEffect },
        Name { "AEHL SDK Control" },
        Category { "AE Hot Loader Diagnostic" },
        CodeMacARM64 { "EffectMain" },
        AE_PiPL_Version { 2, 0 },
        AE_Effect_Spec_Version { 13, 29 },
        AE_Effect_Version { 0x8001 },
        AE_Effect_Info_Flags { 0 },
        AE_Effect_Global_OutFlags { 0 },
        AE_Effect_Global_OutFlags_2 { 0 },
        AE_Effect_Match_Name { "AEHL.SDK.Control" },
        AE_Reserved_Info { 0 }
    }
};
