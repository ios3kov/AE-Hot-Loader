use after_effects as ae;

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
                out_data
                    .set_return_msg("AE Hot Loader Bridge\rInternal effect-registration bridge.");
            }
            ae::Command::Render {
                in_layer,
                mut out_layer,
            } => {
                out_layer.copy_from(&in_layer, None, None)?;
            }
            _ => {}
        }
        Ok(())
    }
}
