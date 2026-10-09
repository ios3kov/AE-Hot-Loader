// Actual observer, real SDK declarations, owned request files; no Adobe callbacks.
#include "../experiments/startup_calibration/CalibrationObserver.cpp"
#include <iostream>
#include <fstream>
#include <iterator>

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
        const auto own_module = Module(), own_executable = Executable();
        const auto module_before = calibration_module, executable_before = calibration_executable;
        const auto file_bytes = resident_binding::ReadPinned({own_module, resident_binding::Hash([&] {
            std::ifstream in(own_module, std::ios::binary); Require(bool(in));
            return resident_binding::Bytes(std::istreambuf_iterator<char>(in), {});
        }())});
        const auto own_hash = resident_binding::Hash(file_bytes);
        constexpr char digits[] = "0123456789abcdef";
        std::string binary_hash;
        for (unsigned char byte : own_hash) { binary_hash += digits[byte >> 4]; binary_hash += digits[byte & 15]; }
        for (unsigned mode = 0; mode < 14; ++mode) {
            calibration_module = mode >= 12 ? own_module.c_str() : module_before;
            calibration_executable = mode >= 12 ? own_executable.c_str() : executable_before;
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
                (mode == 13 ? binary_hash : std::string(64, '0')) + (mode == 5 ? " trailing\n" : "\n");
            if (mode == 0) Require(std::filesystem::create_directory(path + "/request"));
            else {
                Save("request", mode == 2 ? "broken\n" : request);
                if (mode == 1) Require(chmod((path + "/request").c_str(), 0644) == 0);
            }
            Idle(nullptr, nullptr, nullptr);
            const auto result = Read("result");
            const auto stage = mode <= 1 ? "request-read" : mode == 2 ? "request-parse-fields" :
                mode <= 5 ? "request-parse-contract" : mode == 6 ? "request-token" :
                mode <= 8 ? "request-process" : mode <= 10 ? "request-deadline" : mode == 11 ? "request-module-path" :
                mode == 12 ? "resident-pin-contract" : "resident-image-parse";
            if (result.find(std::string("\nstage=") + stage + "\n") == std::string::npos)
                throw std::runtime_error(std::string("actual Idle refusal lost expected stage ") + stage);
            Require(consumed && !names && result.find("\nstatus=REFUSED\n") != std::string::npos);
            Idle(nullptr, nullptr, nullptr); // One-shot refusal cannot overwrite the result.
            Require(Read("result") == result && !Exists("begin") && !Exists("names-0"));
        }
        DiagnosticStage("resident-text-mismatch");
        diagnostic_difference = {true, 6, 4102, 0x04030201U, 0x04090201U};
        const auto difference_details = DiagnosticDetails();
        Require(difference_details == "mismatch_relative_offset=6\nmismatch_file_offset=4102\nmismatch_expected_word=67305985\nmismatch_actual_word=67699201\n");
        DiagnosticStage("resident-text-read");
        Require(DiagnosticDetails().empty()); // A later error cannot leak stale code details.
#ifdef AEHL_CALIBRATION_DIAGNOSTIC_CLOCK_TEST
        // Actual Idle on owned files with injected clocks; never changes OS time.
        // Normal delivery reaches the deliberate module-path refusal; expired
        // active/sleep/forward-clock and backward-clock requests stop earlier.
        for (unsigned mode=0; mode<5; ++mode) {
            const auto path=base+"/clock-"+std::to_string(mode);
            Require(std::filesystem::create_directory(path) && chmod(path.c_str(),0700)==0);
            calibration_control=path.c_str();calibration_module=module_before;consumed=false;cleanup_ok=true;
            diagnostic_clock={true, mode==0?1002000ULL:mode==4?820000ULL:1180000ULL,
                mode==1?180000ULL:2000ULL,mode==1?181000000000ULL:3000000000ULL,
                mode==1||mode==2?182000000000ULL:4000000000ULL};
            Save("request",std::string("AEHL-CAL-REQUEST-2 ")+calibration_token+" "+
                std::to_string(getpid())+" "+std::to_string(Birth())+
                " 1110 OWNED-STARTUP-REGISTRY-OBSERVATION "+std::string(64,'0')+"\n");
            Idle(nullptr,nullptr,nullptr);
            const auto result=Read("result");
            Require(result.find(std::string("\nstage=")+(mode==0?"request-module-path":"request-deadline")+"\n")!=std::string::npos);
            Require(Exists("request-received") && Exists("request-parsed") && Exists("request-deadline-check"));
            Require(!Exists("request-binding-before") && !Exists("begin") && !names);
            const auto timing=Read("request-deadline-check");
            Require(timing.find("\ndeadline=1110\n")!=std::string::npos &&
                timing.find("\nwall_ms="+std::to_string(diagnostic_clock.wall_ms)+"\n")!=std::string::npos);
            Idle(nullptr,nullptr,nullptr);Require(Read("result")==result && Read("request-deadline-check")==timing);
        }
        diagnostic_clock.enabled=false;
#endif
#ifdef AEHL_REGISTRATION_ROUTE_RESOURCE_MATCH
        for (const auto* ownership : {"OWNED-STARTUP-APPLY-RENDER", "OWNED-STARTUP-QUEUE-CONTROL"}) {
            const auto path=base+"/forbidden-"+std::string(ownership);
            Require(std::filesystem::create_directory(path) && chmod(path.c_str(),0700)==0);
            calibration_control=path.c_str();consumed=false;cleanup_ok=true;
            Save("request",std::string("AEHL-CAL-REQUEST-2 ")+calibration_token+" "+
                std::to_string(getpid())+" "+std::to_string(Birth())+" "+std::to_string(Now()+110)+
                " "+ownership+" "+binary_hash+"\n");
            Idle(nullptr,nullptr,nullptr);
            Require(Read("result").find("\nstage=request-parse-contract\n")!=std::string::npos &&
                !Exists("request-binding-before") && !Exists("begin") && !Exists("names-0") && !names);
        }
#endif
        SuiteCases();
        std::cout << "PASS:14 owned request refusals; 5 owned SDK-acquisition cases; actual Idle stage and replay guards; Adobe_calls=0\n";
#ifdef AEHL_REGISTRATION_ROUTE_RESOURCE_MATCH
        std::cout << "PASS:2 direct contrast-request Apply/queue refusals before resident binding or Backend; Adobe_calls=0\n";
#endif
#ifdef AEHL_CALIBRATION_DIAGNOSTIC_CLOCK_TEST
        std::cout<<"PASS:5 actual Idle clock scenarios; one-shot timing; OS_clock_changes=0; Adobe_calls=0\n";
#endif
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
