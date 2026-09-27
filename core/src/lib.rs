use after_effects as ae;
use std::fs::OpenOptions;
use std::io::Write;
use std::os::raw::c_char;

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
    1
}

#[unsafe(no_mangle)]
pub extern "C" fn AEHotLoader_ImplementationStateABI() -> u64 {
    1
}

#[unsafe(no_mangle)]
pub extern "C" fn AEHotLoader_ImplementationKey(
    output: *mut c_char,
    output_capacity: usize,
) -> i32 {
    if output.is_null() || output_capacity == 0 {
        return -1;
    }

    const KEY: &str = "control";
    let bytes = KEY.as_bytes();
    let count = bytes.len().min(output_capacity.saturating_sub(1));

    unsafe {
        std::ptr::copy_nonoverlapping(bytes.as_ptr(), output.cast::<u8>(), count);
        *output.add(count) = 0;
    }

    0
}
