#include "../experiments/ordinary_discovery/MappedMemoryRead.hpp"
#include <functional>
#include <iostream>
#include <string>
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
#include <sys/mman.h>
#include <unistd.h>
#include <thread>
#endif
using namespace mapped_memory;
static unsigned cases = 0;
static void Check(bool v) { if (!v) throw std::runtime_error("test-assertion"); }
struct Fake : Backend {
    Region mapping{0x1000, 0x10000, 0, 23, 17, 0, 3, 3};
    unsigned queries = 0, copies = 0;
    std::function<void(Fake&)> on_query;
    std::function<void(Fake&, Bytes&)> on_copy;
    Region query(Address) override { ++queries; if (on_query) on_query(*this); return mapping; }
    Bytes copy(Address, std::size_t size) override {
        ++copies; Bytes b(size, 42); if (on_copy) on_copy(*this, b); return b;
    }
};
static void Refuse(const std::function<void(Fake&)>& setup, Address address, std::size_t size,
                   const char* reason, unsigned copies) {
    Fake f; setup(f); Reader reader(f); bool refused = false;
    try { (void)reader.read(address, size); } catch (const std::runtime_error& e) {
        Check(e.what() == std::string(reason)); refused = true;
    }
    Check(refused && f.copies == copies && reader.records().empty());
    const auto queries = f.queries;
    refused = false;
    try { (void)reader.read(0x1000, 8); } catch (const std::runtime_error& e) {
        Check(e.what() == std::string("mapped-read-consumed-failure")); refused = true;
    }
    Check(refused && f.queries == queries && f.copies == copies); ++cases;
}
int main() {
    { Fake f; Reader reader(f); const auto bytes = reader.read(0x1000, 8);
      Check(bytes == Bytes(8, 42) && reader.calls() == 1 && reader.bytes() == 8 &&
            reader.records().size() == 1 && reader.records()[0].mapping.object_id == 23); ++cases; }
    for (const auto& request : std::vector<std::pair<Address, std::size_t>>{
            {0, 8}, {0x1000, 0}, {0x1000, 4097}, {UINT64_MAX - 7, 8}})
        Refuse([](Fake&) {}, request.first, request.second, "mapped-read-invalid-request", 0);
    for (unsigned kind = 0; kind < 5; ++kind) Refuse([kind](Fake& f) {
        if (kind == 0) f.mapping.address = 0;
        if (kind == 1) f.mapping.size = 0;
        if (kind == 2) { f.mapping.address = UINT64_MAX - 7; f.mapping.size = 16; }
        if (kind == 3) f.mapping.address = 0x2000;
        if (kind == 4) f.mapping.size = 4;
    }, 0x1000, 8, "mapped-read-outside-region", 0);
    for (unsigned kind = 0; kind < 6; ++kind) Refuse([kind](Fake& f) {
        if (kind == 0) f.mapping.protection = 0;
        if (kind == 1) { f.mapping.protection = 5; f.mapping.maximum = 7; }
        if (kind == 2) f.mapping.protection = 9;
        if (kind == 3) f.mapping.maximum = 0;
        if (kind == 4) f.mapping.maximum = 11;
        if (kind == 5) f.mapping.depth = 17;
    }, 0x1000, 8, "mapped-read-invalid-protection-or-depth", 0);
    for (unsigned field = 0; field < 6; ++field) Refuse([field](Fake& f) {
        f.on_query = [field](Fake& x) { if (x.queries == 2) {
            if (field == 0) x.mapping.size += 8;
            if (field == 1) x.mapping.offset += 8;
            if (field == 2) x.mapping.object_id++;
            if (field == 3) x.mapping.user_tag++;
            if (field == 4) x.mapping.protection = 1;
            if (field == 5) x.mapping.depth = 1;
        } };
    }, 0x1000, 8, "mapped-read-region-changed", 1);
    for (bool extra : {false, true}) Refuse([extra](Fake& f) {
        f.on_copy = [extra](Fake&, Bytes& b) { if (extra) b.push_back(0); else b.pop_back(); };
    }, 0x1000, 8, "mapped-read-short-or-extra-copy", 1);
    Refuse([](Fake& f) { f.on_query = [](Fake&) { throw std::runtime_error("query-failed"); }; },
           0x1000, 8, "query-failed", 0);
    Refuse([](Fake& f) { f.on_query = [](Fake& x) { if (x.queries == 2) throw std::runtime_error("query-failed"); }; },
           0x1000, 8, "query-failed", 1);
    Refuse([](Fake& f) { f.on_copy = [](Fake&, Bytes&) { throw std::runtime_error("copy-failed"); }; },
           0x1000, 8, "copy-failed", 1);
    { Fake f; Reader reader(f);
      for (unsigned i = 0; i < Reader::kCalls; ++i) (void)reader.read(0x1000, 8);
      bool refused = false;
      try { (void)reader.read(0x1000, 8); } catch (const std::runtime_error& e) {
          Check(e.what() == std::string("mapped-read-budget")); refused = true;
      }
      Check(refused && reader.calls() == 24 && f.copies == 24); ++cases; }
    { Fake f; Reader reader(f);
      for (unsigned i = 0; i < Reader::kBytes / Reader::kChunk; ++i) (void)reader.read(0x1000, Reader::kChunk);
      bool refused = false;
      try { (void)reader.read(0x1000, 1); } catch (const std::runtime_error& e) {
          Check(e.what() == std::string("mapped-read-budget")); refused = true;
      }
      Check(refused && reader.bytes() == 16384 && f.copies == 4); ++cases; }
    std::cout << "MAPPED_MEMORY_CASES=" << cases << " PASS; host_calls=0\n";
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
    const auto page = static_cast<std::size_t>(sysconf(_SC_PAGESIZE)); Check(page > 0);
    void* storage = mmap(nullptr, page * 2, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1, 0);
    Check(storage != MAP_FAILED);
    const auto address = reinterpret_cast<std::uintptr_t>(storage);
    auto* words = static_cast<std::uint64_t*>(storage); words[0] = 0x123456789abcdef0ULL;
    SelfBackend backend; Reader own(backend);
    const auto bytes = own.read(address, 8);
    Check(cleanup_snapshot::Word(bytes, 0, 8) == words[0] && own.records().size() == 1);
    Check(mprotect(static_cast<char*>(storage) + page, page, PROT_NONE) == 0);
    auto native_refuse = [&](Address at, std::size_t size) {
        Reader r(backend); bool refused = false;
        try { (void)r.read(at, size); } catch (const std::exception&) { refused = true; }
        Check(refused && r.records().empty());
    };
    native_refuse(address + page, 8);
    native_refuse(address + page - 4, 8);
    native_refuse(1, 8);
    bool thread_refused = false;
    std::thread thread([&] { Reader r(backend);
        try { (void)r.read(address, 8); } catch (const std::exception&) { thread_refused = true; }
    }); thread.join(); Check(thread_refused);
    Check(munmap(storage, page * 2) == 0);
    std::cout << "OWNED_MAPPED_MEMORY PASS; foreign_reads=0; Adobe_calls=0\n";
#endif
}
