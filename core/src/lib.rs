use after_effects as ae;
use std::fs::OpenOptions;
use std::io::Write;

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
