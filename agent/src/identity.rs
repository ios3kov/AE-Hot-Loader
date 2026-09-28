//! Immutable metadata of this loaded Agent image, not the file currently on disk.
use std::os::raw::c_char;

pub const JSON: &str = env!("AEHL_AGENT_IDENTITY");
pub const BUILD_ID: &str = env!("AEHL_AGENT_BUILD_ID");
pub const COMMIT: &str = env!("AEHL_AGENT_GIT_COMMIT");
pub const SOURCE_CLEAN: &str = env!("AEHL_AGENT_SOURCE_CLEAN");
pub const TARGET: &str = env!("AEHL_AGENT_TARGET");
pub const VERSION: &str = env!("AEHL_AGENT_VERSION");

/// Caller must supply a writable buffer of `capacity` bytes. No truncation:
/// -1 = invalid buffer, -2 = insufficient capacity, 0 = complete NUL-terminated JSON.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn AEHotLoader_AgentBuildIdentity(
    output: *mut c_char,
    capacity: usize,
) -> i32 {
    if output.is_null() || capacity == 0 {
        return -1;
    }
    unsafe { *output = 0 };
    if capacity <= JSON.len() {
        return -2;
    }
    unsafe {
        std::ptr::copy_nonoverlapping(JSON.as_ptr(), output.cast::<u8>(), JSON.len());
        *output.add(JSON.len()) = 0;
    }
    0
}

#[cfg(target_os = "macos")]
unsafe extern "C" {
    fn AEHotLoader_CopyAgentImagePath(output: *mut c_char, capacity: usize) -> i32;
}

/// Same buffer contract as the metadata getter. -3 = image lookup failed.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn AEHotLoader_AgentImagePath(output: *mut c_char, capacity: usize) -> i32 {
    #[cfg(target_os = "macos")]
    unsafe {
        AEHotLoader_CopyAgentImagePath(output, capacity)
    }
    #[cfg(not(target_os = "macos"))]
    {
        let _ = (output, capacity);
        -3
    }
}
