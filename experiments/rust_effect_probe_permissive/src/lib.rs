use std::ffi::{c_char, c_void};

type AErr = i32;
type ALong = i32;
type PfErr = i32;
type PfCmd = i32;

#[repr(C)]
pub struct PF_PluginData {
    _unused: [u8; 0],
}
type PFPluginDataPtr = *mut PF_PluginData;

#[repr(C)]
pub struct SPBasicSuite {
    _unused: [u8; 0],
}
#[repr(C)]
pub struct PFInData {
    _unused: [u8; 0],
}
#[repr(C)]
pub struct PFOutData {
    _unused: [u8; 0],
}
#[repr(C)]
pub struct PFParamDef {
    _unused: [u8; 0],
}
#[repr(C)]
pub struct PFLayerDef {
    _unused: [u8; 0],
}

type PFPluginDataCB2 = Option<
    unsafe extern "C" fn(
        PFPluginDataPtr,
        *const u8,
        *const u8,
        *const u8,
        *const u8,
        ALong,
        ALong,
        ALong,
        ALong,
        *const u8,
    ) -> AErr,
>;

const AE_EFFECT_KIND: ALong = i32::from_be_bytes(*b"eFKT");
const API_MAJOR: ALong = 13;
const API_MINOR: ALong = 29;
const RESERVED_INFO: ALong = 8;

static NAME: &[u8] = b"AE Hot Loader Rust Probe Permissive\0";
static MATCH_NAME: &[u8] = b"OS3KOV.AEHotLoader.RustProbe.Permissive\0";
static CATEGORY: &[u8] = b"AE Hot Loader Diagnostic\0";
static ENTRYPOINT: &[u8] = b"EffectMain\0";
static SUPPORT_URL: &[u8] = b"https://github.com/ios3kov/AE-Hot-Loader\0";

#[unsafe(no_mangle)]
#[allow(non_snake_case)]
pub unsafe extern "C" fn PluginDataEntryFunction2(
    in_ptr: PFPluginDataPtr,
    in_callback: PFPluginDataCB2,
    _in_basic_suite: *const SPBasicSuite,
    _in_host_name: *const c_char,
    _in_host_version: *const c_char,
) -> PfErr {
    let Some(callback) = in_callback else {
        return -1;
    };

    unsafe {
        callback(
            in_ptr,
            NAME.as_ptr(),
            MATCH_NAME.as_ptr(),
            CATEGORY.as_ptr(),
            ENTRYPOINT.as_ptr(),
            AE_EFFECT_KIND,
            API_MAJOR,
            API_MINOR,
            RESERVED_INFO,
            SUPPORT_URL.as_ptr(),
        )
    }
}

#[unsafe(no_mangle)]
#[allow(non_snake_case)]
pub unsafe extern "C" fn EffectMain(
    _cmd: PfCmd,
    _in_data: *mut PFInData,
    _out_data: *mut PFOutData,
    _params: *mut *mut PFParamDef,
    _output: *mut PFLayerDef,
    _extra: *mut c_void,
) -> PfErr {
    0
}
