// Compile with the actual Adobe SDK headers; no guessed PF_OutData layout.
#define DYNAMIC_REGISTRATION 0
#include "../experiments/ordinary_discovery/RegistrationPair.cpp"
#include <cassert>

int main() {
    PF_OutData out{};
    out.num_params = -1;
    assert(EffectMain(PF_Cmd_PARAMS_SETUP, nullptr, &out, nullptr, nullptr, nullptr) == PF_Err_NONE);
    assert(out.num_params == 1);
    out.out_flags = ~0;
    out.out_flags2 = ~0;
    assert(EffectMain(PF_Cmd_GLOBAL_SETUP, nullptr, &out, nullptr, nullptr, nullptr) == PF_Err_NONE);
    assert(out.my_version == 0x8001 && out.out_flags == 0 && out.out_flags2 == 0);
    assert(EffectMain(PF_Cmd_PARAMS_SETUP, nullptr, nullptr, nullptr, nullptr, nullptr) == PF_Err_BAD_CALLBACK_PARAM);
    assert(EffectMain(PF_Cmd_RENDER, nullptr, &out, nullptr, nullptr, nullptr) != PF_Err_NONE);
    assert(EffectMain(PF_Cmd_GLOBAL_SETDOWN, nullptr, &out, nullptr, nullptr, nullptr) == PF_Err_NONE);
}
