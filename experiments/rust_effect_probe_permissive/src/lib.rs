use std::ffi::{CStr, c_char, c_void};
use std::fs::OpenOptions;
use std::io::Write;

fn log_line(line: &str) {
    if let Ok(mut file) = OpenOptions::new()
        .create(true)
        .append(true)
        .open("/tmp/ae-hot-loader-rust-probe-permissive.log")
    {
        let _ = writeln!(file, "{line}");
    }
}

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
    in_basic_suite: *const SPBasicSuite,
    in_host_name: *const c_char,
    in_host_version: *const c_char,
) -> PfErr {
    let host_name = if in_host_name.is_null() {
        "(null)".to_string()
    } else {
        unsafe { CStr::from_ptr(in_host_name) }
            .to_string_lossy()
            .into_owned()
    };
    let host_version = if in_host_version.is_null() {
        "(null)".to_string()
    } else {
        unsafe { CStr::from_ptr(in_host_version) }
            .to_string_lossy()
            .into_owned()
    };

    log_line(&format!(
        "ENTRY in_ptr={in_ptr:p} callback_present={} suite={in_basic_suite:p} host={host_name:?} version={host_version:?}",
        in_callback.is_some()
    ));

    let Some(callback) = in_callback else {
        log_line("NO_CALLBACK");
        return -1;
    };

    let result = unsafe {
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
    };

    log_line(&format!("REGISTRATION_RESULT={result}"));
    result
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
