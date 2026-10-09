// Actual observer, real SDK declarations, owned request files; no Adobe callbacks.
#include "../experiments/startup_calibration/CalibrationObserver.cpp"
#include <iostream>

namespace {
int suite_mode = 0, acquires = 0, releases = 0;
AEGP_EffectSuite5 owned_suite{};
SPErr AcquireOwned(const char*, int32, const void** value) {
    ++acquires;
    *value = suite_mode == 1 || suite_mode == 2 ? nullptr : &owned_suite;
    return suite_mode == 1 || suite_mode == 3 ? -123 : 0;
}
SPErr ReleaseOwned(const char*, int32) { ++releases; return 0; }
void SuiteCases() {
    SPBasicSuite provider{}; provider.AcquireSuite = AcquireOwned; provider.ReleaseSuite = ReleaseOwned;
    for (suite_mode = 0; suite_mode < 5; ++suite_mode) {
        basic = suite_mode == 4 ? nullptr : &provider;
        cleanup_ok = true; acquires = releases = 0;
        bool refused = false;
        try {
            Suite<AEGP_EffectSuite5> actual(kAEGPEffectSuite, kAEGPEffectSuiteVersion5);
            Require(actual.value == &owned_suite);
        } catch (...) { refused = true; }
        Require(refused == (suite_mode != 0));
        Require(std::string(diagnostic_stage) == (suite_mode == 2 ? "sdk-suite-empty" : "sdk-suite-acquire"));
        Require(std::strcmp(diagnostic_suite, kAEGPEffectSuite) == 0 && diagnostic_suite_version == kAEGPEffectSuiteVersion5);
        Require(diagnostic_host_error_known == (suite_mode != 4));
        if (suite_mode != 4) Require(diagnostic_host_error == (suite_mode == 1 || suite_mode == 3 ? -123 : 0));
        Require(acquires == (suite_mode == 4 ? 0 : 1) && releases == (suite_mode == 0 ? 1 : 0));
        Require(cleanup_ok == (suite_mode != 3)); // A pointer returned with error has unknown ownership.
    }
    basic = nullptr;
}
}

int main(int argc, char** argv) {
    try {
        Require(argc == 2);
        const auto base = std::filesystem::canonical(argv[1]).string();
        for (unsigned mode = 0; mode < 12; ++mode) {
            const auto path = base + "/request-" + std::to_string(mode);
            Require(std::filesystem::create_directory(path) && chmod(path.c_str(), 0700) == 0);
            calibration_control = path.c_str();
            consumed = idle_active = false; cleanup_ok = true;
            diagnostic_stage = "idle-registration"; // State left by completed startup.
            const auto token = mode == 6 ? "wrong-token" : calibration_token;
            const auto pid = static_cast<std::uint64_t>(getpid()) + (mode == 7 ? 1 : 0);
            const auto born = Birth() + (mode == 8 ? 1 : 0);
            const auto deadline = Now() + (mode == 9 ? 0 : mode == 10 ? 122 : 110);
            const auto schema = mode == 3 ? "WRONG-SCHEMA" : "AEHL-CAL-REQUEST-2";
            const auto ownership = mode == 4 ? "WRONG-OWNERSHIP" : "OWNED-STARTUP-REGISTRY-OBSERVATION";
            const auto request = std::string(schema) + " " + token + " " + std::to_string(pid) + " " +
                std::to_string(born) + " " + std::to_string(deadline) + " " + ownership + " " +
                std::string(64, '0') + (mode == 5 ? " trailing\n" : "\n");
            if (mode == 0) Require(std::filesystem::create_directory(path + "/request"));
            else {
                Save("request", mode == 2 ? "broken\n" : request);
                if (mode == 1) Require(chmod((path + "/request").c_str(), 0644) == 0);
            }
            Idle(nullptr, nullptr, nullptr);
            const auto result = Read("result");
            const auto stage = mode <= 1 ? "request-read" : mode == 2 ? "request-parse-fields" :
                mode <= 5 ? "request-parse-contract" : mode == 6 ? "request-token" :
                mode <= 8 ? "request-process" : mode <= 10 ? "request-deadline" : "request-module-path";
            if (result.find(std::string("\nstage=") + stage + "\n") == std::string::npos)
                throw std::runtime_error(std::string("actual Idle refusal lost expected stage ") + stage);
            Require(consumed && !names && result.find("\nstatus=REFUSED\n") != std::string::npos);
            Idle(nullptr, nullptr, nullptr); // One-shot refusal cannot overwrite the result.
            Require(Read("result") == result && !Exists("begin") && !Exists("names-0"));
        }
        SuiteCases();
        std::cout << "PASS:12 owned request refusals; 5 owned SDK-acquisition cases; actual Idle stage and replay guards; Adobe_calls=0\n";
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
