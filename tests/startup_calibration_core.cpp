#include "../experiments/startup_calibration/CalibrationCore.hpp"
#include "../experiments/startup_calibration/MarkerCore.hpp"
#include "../experiments/startup_calibration/NameProjection.hpp"
#include <functional>
#include <iostream>
#include <stdexcept>
using namespace startup_calibration;
void Check(bool value) { if (!value) throw std::runtime_error("calibration assertion"); }
struct Fake {
    std::uint64_t now = 1000; bool main = true, consume = true, begin = true, create = true, apply = true, dispose = true, identity = true;
    std::int64_t revision = 17; int creates = 0, applies = 0, disposes = 0, revisions = 0, counts = 0;
    int expiry_on_create = 0, changed_revision = 0, changed_count = 0;
    std::int32_t reverse = -13; std::vector<std::int32_t> keys{31, -13, 991};
    int declared = 3; bool cycle = false, duplicate = false, absent = false, thrown = false;
    std::function<void()> nested;
    std::uint64_t Now() { return now; } bool MainThread() { return main; }
    bool Consume() { return consume; }
    bool VerifyBuild() { return identity; }
    std::int64_t BlankProjectRevision() { return ++revisions > 1 && changed_revision ? revision + 1 : revision; }
    int Count() { if (nested) { auto callback = nested; nested = {}; callback(); }
        return ++counts > 1 && changed_count ? declared + 1 : declared; }
    std::int32_t Next(std::int32_t cursor) {
        if (thrown) throw std::runtime_error("mock SDK error");
        if (cycle && cursor) return cursor;
        if (!cursor) return keys.front();
        auto it = std::find(keys.begin(), keys.end(), cursor);
        return it == keys.end() || ++it == keys.end() ? 0 : *it;
    }
    std::string Match(std::int32_t key) { return !absent && (key == -13 || duplicate) ? "marker" : "other"; }
    std::string Target() { return "marker"; }
    bool BeforeMutation() { return begin; }
    bool CreateFixture() { ++creates; if (expiry_on_create) now = 1201; return create; }
    bool Apply(std::int32_t key) { ++applies; Check(key == -13); return apply; }
    std::int32_t Reverse() { return reverse; }
    bool Dispose() { ++disposes; return dispose; }
};
struct NameFake : Fake {
    bool allowed = true, display_only = false, all_own = false, expire_during = false;
    std::string Match(std::int32_t key) { return key == -13 && !display_only && !absent ?
        "AEHL.Marker.target" : "unrelated"; }
    std::string Name(std::int32_t key) {
        if (expire_during) allowed=false;
        return key==-13 || all_own ? "own-display" : "third-party-name-must-not-be-retained";
    }
    bool ObservationAllowed() { return main && allowed; }
};
void NameCases() {
    int cases=0;
    const auto observe=[](auto& b) { return startup_names::Observe(b,"own-display","AEHL.Marker.target"); };
    { NameFake b; const auto s=observe(b); Check(s.complete && s.exact==1 && s.own.size()==1 &&
        s.own[0].key==-13 && s.own[0].name=="own-display" && s.traversed==3 && b.creates==0 && b.applies==0); ++cases; }
    { NameFake b; b.display_only=true; const auto s=observe(b); Check(s.complete && s.exact==0 && s.own.size()==1 &&
        b.applies==0); ++cases; }
    for (int mode=0;mode<9;++mode) {
        NameFake b;
        switch(mode) {
        case 0:b.main=false;break;
        case 1:b.declared=0;break;
        case 2:b.declared=8193;break;
        case 3:b.cycle=true;break;
        case 4:b.declared=4;break;
        case 5:b.declared=2;break;
        case 6:b.changed_count=1;break;
        case 7:b.changed_revision=1;break;
        case 8:b.expire_during=true;break;
        }
        Check(!observe(b).complete && b.creates==0 && b.applies==0);++cases;
    }
    { startup_names::Schedule s(100); Check(!s.Due(99) && s.Due(100)); s.Advance();
        Check(!s.Due(1099) && s.Due(1100));s.Advance();Check(!s.Due(3099) && s.Due(9000));
        s.Advance();s.Advance();Check(s.Done() && !s.Due(9001));++cases; }
    { NameFake b; b.absent=true; const auto first=observe(b);b.absent=false;const auto second=observe(b);
        Check(first.complete && first.exact==0 && second.complete && second.exact==1 && b.applies==0);++cases; }
    { NameFake b;b.keys.clear();for(int i=1;i<=17;++i)b.keys.push_back(i);b.declared=17;b.all_own=true;
        const auto s=observe(b);Check(!s.complete && s.own.size()==16 &&
            std::string(s.stage)=="name-observation-own-bound" && b.applies==0);++cases; }
    { NameFake b;b.thrown=true;bool caught=false;try { observe(b); } catch (...) { caught=true; }
        Check(caught && b.applies==0 && b.creates==0);++cases; }
    std::cout << "NAME_PROJECTION_CASES=" << cases << " PASS; Adobe_calls=0; apply=NOT_RUN\n";
}
int main(int argc, char** argv) {
    try {
        if (argc==2 && std::string(argv[1])=="names") { NameCases();return 0; }
        if (argc == 2 && std::string(argv[1]) == "pixels") {
            std::vector<unsigned char> bytes(19 * 4 * 11 + 11 * 7, 0xA5);
            Check(startup_marker::Render(bytes.data(), 19, 11, 83, 0x345678));
            std::cout.write(reinterpret_cast<char*>(bytes.data()), bytes.size()); return 0;
        }
        int cases = 0;
        const Authorization good{"test-token", 123, 777, 1100, true};
        { Once once; Fake backend; auto result = once.Run(good, good, backend);
          Check(result.outcome == Outcome::ListedApplied && result.key == -13 && backend.disposes == 1);
          Check(once.Run(good, good, backend).outcome == Outcome::Refused && backend.applies == 1); ++cases; }
        for (int mode = 0; mode < 20; ++mode) {
            Once once; Fake backend; auto request = good;
            switch (mode) {
            case 0: backend.main = false; break;
            case 1: request.token.clear(); break;
            case 2: request.token = "wrong"; break;
            case 3: request.pid = 124; break;
            case 4: request.birth = 778; break;
            case 5: request.owned_blank_project = false; break;
            case 6: request.deadline = 1000; break;
            case 7: request.deadline = 1121; break;
            case 8: backend.consume = false; break;
            case 9: backend.revision = 0; break;
            case 10: backend.declared = 0; break;
            case 11: backend.declared = 8193; break;
            case 12: backend.cycle = true; break;
            case 13: backend.duplicate = true; break;
            case 14: backend.absent = true; break;
            case 15: backend.changed_revision = 1; break;
            case 16: backend.changed_count = 1; break;
            case 17: backend.begin = false; break;
            case 18: backend.declared = 2; break;
            case 19: backend.declared = 4; break;
            }
            const auto refused = once.Run(request, good, backend);
            Check(refused.outcome == Outcome::Refused && backend.creates == 0 && backend.applies == 0);
            // Preserve every rejection while making the live pre-mutation cause distinguishable.
            const char* expected = nullptr;
            switch (mode) {
            case 10: case 11: expected = "enumeration-count-range"; break;
            case 12: expected = "enumeration-repeated-key"; break;
            case 13: expected = "enumeration-marker-duplicate"; break;
            case 14: expected = "enumeration-marker-absent"; break;
            case 15: expected = "enumeration-project-changed"; break;
            case 16: expected = "enumeration-count-changed"; break;
            case 18: expected = "enumeration-missing-end"; break;
            case 19: expected = "enumeration-early-end"; break;
            }
            if (expected) Check(std::string(refused.stage) == expected);
            Check(once.Run(good, good, backend).outcome == Outcome::Refused && backend.applies == 0); ++cases;
        }
        for (int mode = 0; mode < 6; ++mode) {
            Once once; Fake backend;
            switch (mode) {
            case 0: backend.create = false; break;
            case 1: backend.apply = false; break;
            case 2: backend.reverse = 31; break;
            case 3: backend.dispose = false; break;
            case 4: backend.expiry_on_create = 1; break;
            case 5: backend.identity = false; break;
            }
            Check(once.Run(good, good, backend).outcome == Outcome::PartialUnknown && backend.creates == 1);
            once.Run(good, good, backend); Check(backend.creates == 1); ++cases;
        }
        { Once once; Fake backend;
          backend.nested = [&]() { Check(once.Run(good, good, backend).outcome == Outcome::Refused); };
          Check(once.Run(good, good, backend).outcome == Outcome::ListedApplied && backend.applies == 1); ++cases; }
        { Once once; Fake backend; backend.thrown = true; bool caught = false;
          try { once.Run(good, good, backend); } catch (...) { caught = true; }
          Check(caught && once.Run(good, good, backend).outcome == Outcome::Refused && backend.creates == 0); ++cases; }
        for (int mode = 0; mode < 7; ++mode) {
            std::vector<unsigned char> bytes(128, 0xA5), before = bytes;
            const auto okay = startup_marker::Render(mode == 0 ? nullptr : bytes.data(),
                mode == 1 ? 0 : mode == 2 ? 4097 : 4, mode == 3 ? -1 : 2,
                mode == 4 ? 15 : mode == 5 ? -16 : mode == 6 ? 65537 : 16, 0x345678);
            Check(!okay && bytes == before); ++cases;
        }
        std::cout << "CALIBRATION_CORE_CASES=" << cases << " PASS; Adobe_calls=0; render=NOT_RUN\n";
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
