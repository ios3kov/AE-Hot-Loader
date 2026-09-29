#include "../experiments/ordinary_discovery/ScopedDiscoveryGate.hpp"
#include <cassert>
#include <iostream>

namespace {
struct Fixture {
    scoped::fs::path base;
    scoped::Config config;
    int calls = 0, reads = 0;
    Fixture() {
        char path[] = "/private/tmp/aehl-scoped-tests-XXXXXX";
        const char* made = mkdtemp(path);
        assert(made);
        base = made;
        const auto root = base / "scan-root";
        const auto evidence = base / "evidence";
        scoped::fs::create_directories(root / "Fixture.plugin/Contents/Resources");
        scoped::fs::create_directory(evidence);
        chmod(evidence.c_str(), 0700);
        config = {"test-build", "test-source", "test-token", "/owned/test-host",
                  root.string(), "Fixture.plugin", evidence.string(), "AEHL.Embedded.test",
                  {{"Contents/Resources/Fixture.rsrc", scoped::Hash("bytes")}}};
        const auto file = root / "Fixture.plugin/Contents/Resources/Fixture.rsrc";
        const int fd = open(file.c_str(), O_WRONLY | O_CREAT | O_EXCL, 0600);
        assert(fd >= 0 && write(fd, "bytes", 5) == 5 && close(fd) == 0);
    }
    ~Fixture() { scoped::fs::remove_all(base); }
    std::string snapshot() {
        ++reads;
        return reads == 1 ? "AEHL-SNAPSHOT-1\n1\nADBE.Test\n" :
                            "AEHL-SNAPSHOT-1\n1\nADBE.Test\nAEHL.Embedded.test\n";
    }
    int load(const char* root) {
        ++calls;
        assert(root == config.root);
        return 1;
    }
    void run() {
        scoped::Run(config, scoped::Request(config, getpid()), getpid(),
                    config.host_executable, config.token,
                    [&] { return snapshot(); }, [&](const char* root) { return load(root); });
    }
};
template<class F> void Reject(F action) {
    bool rejected = false;
    try { action(); } catch (const std::exception&) { rejected = true; }
    assert(rejected);
}
}

int main() {
    int cases = 0;
    { Fixture f; f.run(); assert(f.calls == 1 && f.reads == 2);
      assert(scoped::Read(f.base / "evidence/result.txt", 4096).find("status=PASS\n") == 0);
      Reject([&] { f.run(); }); assert(f.calls == 1); ++cases; }
    for (int kind = 0; kind < 3; ++kind) {
        Fixture f;
        Reject([&] { scoped::Run(f.config, scoped::Request(f.config, getpid()),
            kind == 0 ? getpid() + 1 : getpid(),
            kind == 1 ? "/wrong/host" : f.config.host_executable,
            kind == 2 ? "wrong-token" : f.config.token,
            [&] { return f.snapshot(); }, [&](const char* root) { return f.load(root); }); });
        assert(f.calls == 0 && f.reads == 0); ++cases;
    }
    for (int kind = 0; kind < 5; ++kind) {
        Fixture f;
        const auto resource = f.base / "scan-root/Fixture.plugin/Contents/Resources/Fixture.rsrc";
        if (kind == 0) scoped::fs::create_directory(f.base / "scan-root/Extra.plugin");
        if (kind == 1) scoped::fs::create_directory(f.base / "scan-root/Fixture.plugin/Extra");
        if (kind == 2) scoped::fs::create_symlink(resource, f.base / "scan-root/Fixture.plugin/link");
        if (kind == 3) { const int fd = open(resource.c_str(), O_WRONLY | O_TRUNC);
                         assert(fd >= 0 && close(fd) == 0); }
        if (kind == 4) scoped::fs::create_hard_link(resource, f.base / "linked-resource");
        Reject([&] { f.run(); }); assert(f.calls == 0 && f.reads == 0); ++cases;
    }
    { Fixture f;
      Reject([&] { scoped::Run(f.config, scoped::Request(f.config, getpid()), getpid(),
          f.config.host_executable, f.config.token,
          [] { return "AEHL-SNAPSHOT-1\n1\nAEHL.Embedded.test\n"; },
          [&](const char* root) { return f.load(root); }); });
      assert(f.calls == 0); ++cases; }
    { Fixture f;
      Reject([&] { scoped::Run(f.config, scoped::Request(f.config, getpid()), getpid(),
          f.config.host_executable, f.config.token, [] { return "BLOCKED"; },
          [&](const char* root) { return f.load(root); }); });
      assert(f.calls == 0); ++cases; }
    { Fixture f;
      Reject([&] { scoped::Run(f.config, scoped::Request(f.config, getpid()), getpid(),
          f.config.host_executable, f.config.token, [&] {
              scoped::fs::create_directory(f.base / "scan-root/unexpected");
              return f.snapshot(); }, [&](const char* root) { return f.load(root); }); });
      assert(f.calls == 0); ++cases; }
    for (int kind = 0; kind < 3; ++kind) {
        Fixture f;
        Reject([&] { scoped::Run(f.config, scoped::Request(f.config, getpid()), getpid(),
            f.config.host_executable, f.config.token, [&] {
                auto value = f.snapshot();
                if (f.reads == 2 && kind == 0) value += "unexpected\n";
                if (f.reads == 2 && kind == 1) value.replace(value.find("\n1\n"), 3, "\n2\n");
                return value;
            }, [&](const char* root) { f.load(root); return kind == 2 ? -3007 : 1; }); });
        assert(f.calls == 1 && f.reads == 2);
        assert(scoped::Read(f.base / "evidence/result.txt", 4096).find("status=FAIL\n") == 0);
        Reject([&] { f.run(); }); assert(f.calls == 1); ++cases;
    }
    std::cout << "PASS: " << cases << " scoped discovery guard cases (mock loader, no AE)\n";
}
