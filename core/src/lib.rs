use after_effects as ae;
use std::fs::OpenOptions;
use std::io::Write;
use std::os::raw::c_char;
use std::sync::atomic::{AtomicU64, AtomicUsize, Ordering};
use std::thread;
use std::time::Duration;

const HOT_RELOAD_IMPLEMENTATION_ABI: u32 = 2;
const HOT_RELOAD_STATE_ABI: u64 = 1;
const HOT_RELOAD_IMPLEMENTATION_KEY: &str = "control";

static HOT_RELOAD_GENERATION: AtomicU64 = AtomicU64::new(0);
static BUSY_TEST_RELOAD_CALLBACK: AtomicUsize = AtomicUsize::new(0);

type BusyTestReloadFn = unsafe extern "C" fn(*mut c_char, usize) -> i32;

const IMPLEMENTATION_LABEL: &str = match option_env!("AE_HOT_LOADER_IMPL_LABEL") {
    Some(value) => value,
    None => "default-v1",
};

fn log_impl(event: &str) {
    if let Ok(mut file) = OpenOptions::new()
        .create(true)
        .append(true)
        .open("/tmp/ae-hot-loader-implementation.log")
    {
        let _ = writeln!(file, "{IMPLEMENTATION_LABEL}: {event}");
    }
}

fn run_busy_reload_selftest() {
    let raw = BUSY_TEST_RELOAD_CALLBACK.load(Ordering::Acquire);
    if raw == 0 {
        log_impl("BusySelfTest callback missing");
        return;
    }

    let reload: BusyTestReloadFn = unsafe { std::mem::transmute(raw) };
    let mut message = [0i8; 2048];
    let result = unsafe { reload(message.as_mut_ptr(), message.len()) };
    let len = message
        .iter()
        .position(|&value| value == 0)
        .unwrap_or(message.len());
    let bytes = unsafe { std::slice::from_raw_parts(message.as_ptr().cast::<u8>(), len) };
    let detail = String::from_utf8_lossy(bytes);
    log_impl(&format!("BusySelfTest result={result} message={detail}"));
}

#[derive(Eq, PartialEq, Hash, Clone, Copy, Debug)]
enum Params {}

#[derive(Default)]
struct Plugin;

ae::define_effect!(Plugin, (), Params);

impl AdobePluginGlobal for Plugin {
    fn params_setup(
        &self,
        _: &mut ae::Parameters<Params>,
        _: ae::InData,
        _: ae::OutData,
    ) -> Result<(), Error> {
        Ok(())
    }

    fn handle_command(
        &mut self,
        cmd: ae::Command,
        _: ae::InData,
        mut out_data: ae::OutData,
        _: &mut ae::Parameters<Params>,
    ) -> Result<(), ae::Error> {
        match cmd {
            ae::Command::About => {
                log_impl("About");
                out_data.set_return_msg(&format!(
                    "AE Hot Loader Control Implementation\rBuild: {IMPLEMENTATION_LABEL}"
                ));
            }
            ae::Command::Render {
                in_layer,
                mut out_layer,
            } => {
                // Live-gate hook: when armed by STAGE_BUSY_TEST.command, exactly
                // one render call is held long enough to attempt a concurrent reload.
                // The sentinel is consumed atomically by the first render that sees it.
                if std::fs::remove_file("/tmp/ae-hot-loader-slow-render-once").is_ok() {
                    log_impl("SlowRenderTest begin");
                    let probe = thread::spawn(|| {
                        thread::sleep(Duration::from_millis(750));
                        run_busy_reload_selftest();
                    });
                    thread::sleep(Duration::from_secs(8));
                    let _ = probe.join();
                    log_impl("SlowRenderTest end");
                }
                log_impl("Render");
                out_layer.copy_from(&in_layer, None, None)?;
            }
            _ => {}
        }
        Ok(())
    }
}
#[unsafe(no_mangle)]
pub extern "C" fn AEHotLoader_ImplementationLabel(
    output: *mut c_char,
    output_capacity: usize,
) -> i32 {
    if output.is_null() || output_capacity == 0 {
        return -1;
    }

    let bytes = IMPLEMENTATION_LABEL.as_bytes();
    let count = bytes.len().min(output_capacity.saturating_sub(1));

    unsafe {
        std::ptr::copy_nonoverlapping(bytes.as_ptr(), output.cast::<u8>(), count);
        *output.add(count) = 0;
    }

    0
}

#[unsafe(no_mangle)]
pub extern "C" fn AEHotLoader_ImplementationABI() -> u32 {
    HOT_RELOAD_IMPLEMENTATION_ABI
}

#[unsafe(no_mangle)]
pub extern "C" fn AEHotLoader_ImplementationStateABI() -> u64 {
    HOT_RELOAD_STATE_ABI
}

#[unsafe(no_mangle)]
pub extern "C" fn AEHotLoader_ImplementationKey(
    output: *mut c_char,
    output_capacity: usize,
) -> i32 {
    if output.is_null() || output_capacity == 0 {
        return -1;
    }

    let bytes = HOT_RELOAD_IMPLEMENTATION_KEY.as_bytes();
    let count = bytes.len().min(output_capacity.saturating_sub(1));

    unsafe {
        std::ptr::copy_nonoverlapping(bytes.as_ptr(), output.cast::<u8>(), count);
        *output.add(count) = 0;
    }

    0
}

const HOT_RELOAD_RUNTIME_ABI: &str = env!("AE_HOT_LOADER_RUNTIME_ABI");

#[unsafe(no_mangle)]
pub extern "C" fn AEHotLoader_ImplementationRuntimeABI(
    output: *mut c_char,
    output_capacity: usize,
) -> i32 {
    if output.is_null() || output_capacity == 0 {
        return -1;
    }

    let bytes = HOT_RELOAD_RUNTIME_ABI.as_bytes();
    let count = bytes.len().min(output_capacity.saturating_sub(1));
    unsafe {
        std::ptr::copy_nonoverlapping(bytes.as_ptr(), output.cast::<u8>(), count);
        *output.add(count) = 0;
    }
    0
}

#[unsafe(no_mangle)]
pub extern "C" fn AEHotLoader_SetGeneration(generation: u64) {
    HOT_RELOAD_GENERATION.store(generation, Ordering::Release);
}

#[unsafe(no_mangle)]
pub extern "C" fn AEHotLoader_SetBusyTestReloadCallback(callback: Option<BusyTestReloadFn>) {
    let raw = callback.map(|function| function as usize).unwrap_or(0);
    BUSY_TEST_RELOAD_CALLBACK.store(raw, Ordering::Release);
}
