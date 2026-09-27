use after_effects as ae;

#[derive(Default)]
struct Plugin;

#[derive(Eq, PartialEq, Hash, Clone, Copy, Debug)]
enum Params {
    Dummy,
}

ae::define_effect!(Plugin, (), Params);

impl AdobePluginGlobal for Plugin {
    fn params_setup(
        &self,
        _params: &mut ae::Parameters<Params>,
        _in_data: ae::InData,
        _out_data: ae::OutData,
    ) -> Result<(), ae::Error> {
        Ok(())
    }

    fn handle_command(
        &mut self,
        command: ae::Command,
        _in_data: ae::InData,
        mut out_data: ae::OutData,
        _params: &mut ae::Parameters<Params>,
    ) -> Result<(), ae::Error> {
        if matches!(command, ae::Command::About) {
            out_data.set_return_msg("AE Hot Loader Rust Probe");
        }
        Ok(())
    }
}
