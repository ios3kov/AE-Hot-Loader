// Owned executable control for SDK types/macros. Does not load or call Adobe code.
#include "AE_Effect.h"
#include "AE_PluginData.h"
#include "entry.h"
#include <cstring>
#include <initializer_list>
#include <type_traits>

using Callback2 = A_Err (*)(PF_PluginDataPtr, const A_u_char*, const A_u_char*,
    const A_u_char*, const A_u_char*, A_long, A_long, A_long, A_long, const A_u_char*);
static_assert(std::is_same<Callback2, PF_PluginDataCB2>::value, "SDK callback2 mismatch");

struct OwnedData { A_Err outcome; unsigned calls; };
static OwnedData owned;
static bool fields_ok = true;
static bool equal(const A_u_char* value, const char* expected) {
    return value && std::strcmp(reinterpret_cast<const char*>(value), expected) == 0;
}
static A_Err callback2(PF_PluginDataPtr context, const A_u_char* name,
    const A_u_char* match, const A_u_char* category, const A_u_char* entry,
    A_long kind, A_long major, A_long minor, A_long reserved, const A_u_char* url) {
    // Address identity only. No fabricated Adobe object is dereferenced.
    fields_ok = fields_ok && context == reinterpret_cast<PF_PluginDataPtr>(&owned)
        && equal(name, "Owned") && equal(match, "AEHL.Owned.Contract")
        && equal(category, "Owned controls") && equal(entry, AE_ENTRY_POINT)
        && kind == 'eFKT' && major == PF_AE_PLUG_IN_VERSION
        && minor == PF_AE_PLUG_IN_SUBVERS && reserved == AE_RESERVED_INFO
        && (!url || equal(url, "https://example.invalid/owned"));
    ++owned.calls;
    return owned.outcome;
}
static A_Err callback1(PF_PluginDataPtr context, const A_u_char* name,
    const A_u_char* match, const A_u_char* category, const A_u_char* entry,
    A_long kind, A_long major, A_long minor, A_long reserved) {
    return callback2(context, name, match, category, entry, kind, major, minor, reserved, nullptr);
}
static A_Err entry2(PF_PluginDataPtr context, PF_PluginDataCB2 callback,
    SPBasicSuite*, const char*, const char*) {
    A_Err result = A_Err_NONE;
    PF_REGISTER_EFFECT_EXT2(context, callback, "Owned", "AEHL.Owned.Contract",
        "Owned controls", AE_RESERVED_INFO, AE_ENTRY_POINT, "https://example.invalid/owned");
    return result;
}
static_assert(std::is_same<decltype(&entry2), PluginDataEntryFunction2Ptr>::value,
              "SDK entry2 mismatch");

int main() {
    auto context = reinterpret_cast<PF_PluginDataPtr>(&owned);
    for (A_Err outcome : {A_Err(0), A_Err(42)}) {
        owned.outcome = outcome;
        if (entry2(context, callback2, nullptr, "Owned host", "Owned version") != outcome) return 1;
        A_Err result = A_Err_NONE;
        PF_REGISTER_EFFECT(context, callback1, "Owned", "AEHL.Owned.Contract",
                           "Owned controls", AE_RESERVED_INFO);
        if (result != outcome) return 2;
    }
    return fields_ok && owned.calls == 4 ? 0 : 3;
}
