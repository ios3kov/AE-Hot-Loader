#include "../experiments/ordinary_discovery/RetainedIdentityJournal.hpp"
#include <filesystem>
#include <iostream>

namespace {
using retained_identity::Bytes;
using retained_identity::Address;
unsigned cases = 0;
void Check(bool value) { if (!value) throw std::runtime_error("journal-fixture-assertion"); }
void Put(Bytes& bytes, std::size_t offset, Address value) {
    for (unsigned i = 0; i < 8; ++i)
        bytes.at(offset + i) = static_cast<unsigned char>(value >> (8 * i));
}
struct Owned : mapped_memory::Backend {
    Bytes data = Bytes(0x5000, 0);
    bool fail = false;
    Owned(unsigned count, bool external) {
        Put(data, 0, count ? 0x2000 : 0); Put(data, 8, count ? 0x2000 + count * 0xb0 : 0);
        for (unsigned i = 0; i < count; ++i) {
            const auto base = 0x1000 + i * 0xb0;
            if (external) {
                Put(data, base + 0x90, 0x3000); Put(data, base + 0x98, 255);
                data[base + 0xa7] = 0x80;
                std::fill(data.begin() + 0x2000, data.begin() + 0x20ff, 0xff);
                data[0x2001] = 0;
            } else {
                data[base + 0x90] = 'O'; data[base + 0x91] = 0xff;
                data[base + 0x92] = 0; data[base + 0x93] = 'Z'; data[base + 0xa7] = 4;
            }
        }
    }
    mapped_memory::Region query(Address) override { return {0x1000, 0x5000, 0, 1, 2, 0, 3, 3}; }
    Bytes copy(Address at, std::size_t size) override {
        if (fail && at == 0x3000) throw std::runtime_error("owned-copy-failed");
        Check(at >= 0x1000 && at - 0x1000 + size <= data.size());
        const auto start = data.begin() + at - 0x1000;
        return Bytes(start, start + size);
    }
};
retained_journal::Scope Scope() {
    return {"retained-identity-" + std::string(32, 'a'), std::string(40, 'b'),
            "identity-" + std::string(12, 'c'), std::string(64, 'd'),
            std::string(64, 'e'), std::string(32, 'f'), "owned-fixture", 73, 1, 2, 0x1000};
}
std::string Folder(const std::filesystem::path& base, const std::string& name) {
    const auto path = base / name; std::filesystem::create_directory(path);
    std::filesystem::permissions(path, std::filesystem::perms::owner_all);
    return path.string();
}
template<class F> void Refuse(F action) {
    bool failed = false; try { action(); } catch (const std::exception&) { failed = true; }
    Check(failed);
}
} // namespace

int main(int argc, char** argv) {
    try {
        Check(argc == 2); const std::filesystem::path base(argv[1]);
        for (const auto& sample : {std::make_pair(0U, false), std::make_pair(2U, false),
                                  std::make_pair(8U, true)}) {
            const auto name = sample.first == 0 ? "empty" : sample.first == 2 ? "inline" : "maximum";
            const auto folder = Folder(base, name); retained_journal::Journal journal(folder);
            journal.claim(Scope()); journal.mark_read(); Owned own(sample.first, sample.second);
            retained_capture::Observer observer;
            const auto result = observer.run(retained_identity::Layout::Mee256Arm64, 0x1000, own);
            Check(result.success && result.frames.size() == result.calls);
            journal.save(result); journal.finish(); ++cases;
            Refuse([&] { journal.finish(); }); Refuse([&] { journal.claim(Scope()); }); ++cases;
            retained_journal::Journal replay(folder);
            Refuse([&] { replay.claim(Scope()); }); Refuse([&] { replay.mark_read(); }); ++cases;
        }
        { const auto folder = Folder(base, "failed"); retained_journal::Journal journal(folder);
          journal.claim(Scope()); journal.mark_read(); Owned own(1, true); own.fail = true;
          retained_capture::Observer observer;
          const auto d = observer.run(retained_identity::Layout::Mee256Arm64, 0x1000, own);
          Check(!d.success && d.frames.size() == 2 && d.calls == 3 && d.snapshot.vector.empty());
          journal.save(d); journal.finish(); ++cases; }
        { retained_journal::Journal journal(Folder(base, "order"));
          Refuse([&] { journal.mark_read(); }); Refuse([&] { journal.claim(Scope()); }); ++cases; }
        { retained_journal::Journal journal(Folder(base, "scope")); auto s = Scope(); s.source[0] = 'x';
          Refuse([&] { journal.claim(s); }); Refuse([&] { journal.claim(Scope()); }); ++cases; }
        { retained_journal::Journal journal(Folder(base, "origin")); auto s = Scope(); s.origin = "ae-diagnostic";
          Refuse([&] { journal.claim(s); }); Refuse([&] { journal.claim(Scope()); }); ++cases; }
        { retained_journal::Journal journal(Folder(base, "bad-native"));
          journal.claim(Scope()); journal.mark_read(); retained_capture::Diagnostic d;
          d.success = true; d.calls = 23;
          Refuse([&] { journal.save(d); }); Refuse([&] { journal.finish(); }); ++cases; }
        { auto s = Scope(); s.start_usec = 1000000; Refuse([&] { retained_journal::ScopeBytes(s); }); ++cases; }
        { auto s = Scope(); s.root = 1; Refuse([&] { retained_journal::ScopeBytes(s); }); ++cases; }
        { auto s = Scope(); s.pid = 0; Refuse([&] { retained_journal::ScopeBytes(s); }); ++cases; }
        std::cout << "RETAINED_JOURNAL_CASES=" << cases << " PASS; Adobe_calls=0\n";
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
