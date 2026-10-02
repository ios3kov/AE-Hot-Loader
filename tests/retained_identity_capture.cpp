#include "../experiments/ordinary_discovery/RetainedIdentityCapture.hpp"
#include <functional>
#include <iostream>
#include <map>
#include <algorithm>
#include <thread>
using namespace retained_capture;
namespace {
unsigned cases = 0;
void Check(bool value) { if (!value) throw std::runtime_error("fixture-assertion"); }
void Put(Bytes& bytes, std::size_t at, Address value) {
    for (unsigned i = 0; i < 8; ++i)
        bytes.at(at + i) = static_cast<unsigned char>(value >> (8 * i));
}
constexpr Layout layout = Layout::Mee256Arm64;
struct Fake : mapped_memory::Backend {
    Bytes data = Bytes(0x6000, 0);
    unsigned copies = 0;
    int copy_delta = 0;
    std::map<Address, unsigned> counts;
    std::vector<Address> addresses;
    mapped_memory::Region region{0x1000, 0x6000, 0, 1, 2, 0, 3, 3};
    std::function<void(Fake&, Address, std::size_t)> on_copy;
    std::function<void(Fake&, Address)> on_query;
    Fake(unsigned count = 2, bool external = true) {
        Put(data, 0, count ? 0x2000 : 0); Put(data, 8, count ? 0x2000 + count * 0xb0 : 0);
        for (unsigned i = 0; i < count; ++i) {
            const auto base = 0x1000 + i * 0xb0;
            Put(data, base, 0x9000 + i * 8);
            if (external) {
                Put(data, base + 0x90, 0x4000 + i * 0x100);
                Put(data, base + 0x98, 255);
                data[base + 0xa7] = 0x80;
                std::fill(data.begin() + 0x3000 + i * 0x100,
                          data.begin() + 0x30ff + i * 0x100, 'A' + i);
            } else {
                data[base + 0x90] = 'A' + i; data[base + 0xa7] = 1;
            }
        }
    }
    mapped_memory::Region query(Address address) override {
        if (on_query) on_query(*this, address); return region;
    }
    Bytes copy(Address address, std::size_t size) override {
        ++copies; ++counts[address]; addresses.push_back(address);
        if (on_copy) on_copy(*this, address, size);
        Check(address >= 0x1000 && address - 0x1000 + size <= data.size());
        const auto start = data.begin() + (address - 0x1000);
        Bytes result(start, start + size);
        if (copy_delta < 0) result.pop_back();
        if (copy_delta > 0) result.push_back(0);
        return result;
    }
};
template<class F> void Refuse(const char* reason, F setup) {
    Fake fake; setup(fake); Observer observer;
    const auto r = observer.run(layout, 0x1000, fake);
    Check(!r.success && r.failure == reason && r.snapshot.vector.empty() &&
          r.snapshot.records.empty() && r.snapshot.names.empty() && r.identities.empty() &&
          r.calls <= Observer::kCalls && r.bytes <= Observer::kBytes);
    const auto copies = fake.copies;
    Check(observer.run(layout, 0x1000, fake).failure == "retained-capture-consumed" &&
          fake.copies == copies); ++cases;
}
void Synthetic() {
    for (unsigned count : {0U, 1U, 7U, 8U}) {
        Fake fake(count); Observer observer; const auto r = observer.run(layout, 0x1000, fake);
        Check(r.success && r.failure.empty() && r.identities.size() == count &&
              r.snapshot.records.size() == count * 0xb0 &&
              r.calls == (count ? 6 + 2 * count : 4) &&
              r.bytes == 64 + count * 2 * (0xb0 + 256) && r.reads.size() == r.calls);
        if (count == 8) Check(r.calls == Observer::kCalls && r.bytes == Observer::kBytes);
        const auto copies = fake.copies;
        Check(observer.run(layout, 0x1000, fake).failure == "retained-capture-consumed" &&
              fake.copies == copies); ++cases;
    }
    { Fake fake(8, false); Observer o; const auto r = o.run(layout, 0x1000, fake);
      Check(r.success && r.calls == 6 && r.bytes == 2880 && r.snapshot.names.empty() &&
            r.identities[7].name == Bytes({'H'})); ++cases; }
    { Fake fake(0); Put(fake.data, 0, 0x2000); Put(fake.data, 8, 0x2000); Observer o;
      Check(o.run(layout, 0x1000, fake).success && !fake.counts.count(0x2000)); ++cases; }
    { Fake fake; Put(fake.data, 0x1000 + 0xb0 + 0x90, 0x4000); Observer o;
      const auto r = o.run(layout, 0x1000, fake);
      Check(r.success && r.identities[0].name == r.identities[1].name &&
            fake.counts[0x4000] == 4); ++cases; }
    for (Address root : {Address(0), Address(0x1001), UINT64_MAX - 7}) {
        Fake fake; Observer o; const auto r = o.run(layout, root, fake);
        Check(r.failure == "retained-capture-invalid-root" && fake.copies == 0 &&
              o.run(layout, 0x1000, fake).failure == "retained-capture-consumed"); ++cases;
    }
    { Fake fake; Observer o; const auto r = o.run(static_cast<Layout>(0), 0x1000, fake);
      Check(r.failure == "unsupported layout" && fake.copies == 0 &&
            o.run(layout, 0x1000, fake).failure == "retained-capture-consumed"); ++cases; }
    { Fake fake; Observer o; Diagnostic a, b;
      std::thread first([&] { a = o.run(layout, 0x1000, fake); });
      std::thread second([&] { b = o.run(layout, 0x1000, fake); });
      first.join(); second.join();
      Check(a.success != b.success && (a.success ? b.failure : a.failure) ==
            "retained-capture-consumed" && fake.copies == 10); ++cases; }
    Refuse("retained-capture-invalid-vector", [](Fake& f) { Put(f.data, 0, 0); });
    Refuse("retained-capture-invalid-vector", [](Fake& f) { Put(f.data, 8, 0); });
    Refuse("retained-capture-invalid-vector", [](Fake& f) { Put(f.data, 0, 0x2001); });
    Refuse("retained-capture-invalid-vector", [](Fake& f) { Put(f.data, 8, 0x2161); });
    Refuse("retained-capture-invalid-vector", [](Fake& f) { Put(f.data, 8, 0x2168); });
    Refuse("retained-capture-invalid-vector", [](Fake& f) { Put(f.data, 8, 0x2000 + 9 * 0xb0); });
    Refuse("retained-capture-record-root-overlap", [](Fake& f) {
        Put(f.data, 0, 0x1000); Put(f.data, 8, 0x10b0); });
    Refuse("external name length limit", [](Fake& f) { Put(f.data, 0x1098, 256); });
    Refuse("external name address", [](Fake& f) { Put(f.data, 0x1090, 0); });
    Refuse("external name range overflow", [](Fake& f) { Put(f.data, 0x1090, UINT64_MAX); });
    Refuse("retained-capture-name-state-overlap", [](Fake& f) { Put(f.data, 0x1090, 0x1008); });
    Refuse("retained-capture-name-state-overlap", [](Fake& f) { Put(f.data, 0x1090, 0x20b0); });
    Refuse("inline name length", [](Fake& f) { f.data[0x10a7] = 23; });
    Refuse("inline name terminator", [](Fake& f) {
        f.data[0x10a7] = 1; f.data[0x1091] = 'x'; });
    Refuse("external name terminator", [](Fake& f) { f.data[0x30ff] = 'x'; });
    Refuse("mapped-read-outside-region", [](Fake& f) { f.region.size = 8; });
    Refuse("mapped-read-invalid-protection-or-depth", [](Fake& f) { f.region.protection = 0; });
    Refuse("mapped-read-invalid-protection-or-depth", [](Fake& f) { f.region.protection = 5; });
    Refuse("mapped-read-outside-region", [](Fake& f) {
        f.on_query = [](Fake& x, Address a) { if (a == 0x4000) x.region.size = 0x3080; }; });
    Refuse("mapped-read-region-changed", [](Fake& f) {
        f.on_query = [](Fake& x, Address) { ++x.region.object_id; }; });
    Refuse("retained-capture-mapping-changed", [](Fake& f) {
        // Apply the change between completed reads, not inside one copy.
        f.on_query = [](Fake& x, Address a) {
            if (a == 0x4100) x.region.object_id = 3;
        };
    });
    Refuse("mapped-read-short-or-extra-copy", [](Fake& f) { f.copy_delta = -1; });
    Refuse("mapped-read-short-or-extra-copy", [](Fake& f) { f.copy_delta = 1; });
    Refuse("mapped-read-short-or-extra-copy", [](Fake& f) {
        f.on_copy = [](Fake& x, Address a, std::size_t) {
            if (a == 0x2000) x.copy_delta = -1;
        }; });
    Refuse("mapped-read-short-or-extra-copy", [](Fake& f) {
        f.on_copy = [](Fake& x, Address a, std::size_t) {
            if (a == 0x4000) x.copy_delta = -1;
        }; });
    for (unsigned read : {2U, 3U, 4U})
        Refuse("retained-capture-vector-changed", [read](Fake& f) {
            f.on_copy = [read](Fake& x, Address a, std::size_t) {
                if (a == 0x1000 && x.counts[a] == read) Put(x.data, 0, 0x3000);
            }; });
    Refuse("retained-capture-records-changed", [](Fake& f) {
        f.on_copy = [](Fake& x, Address a, std::size_t) {
            if (a == 0x2000 && x.counts[a] == 2) Put(x.data, 0x1000, 0xbeef);
        }; });
    Refuse("retained-capture-records-changed", [](Fake& f) {
        f.on_copy = [](Fake& x, Address a, std::size_t) {
            if (a == 0x2000 && x.counts[a] == 2) Put(x.data, 0x1090, 0x6000);
        }; });
    Refuse("retained-capture-name-changed", [](Fake& f) {
        f.on_copy = [](Fake& x, Address a, std::size_t) {
            if (a == 0x4000 && x.counts[a] == 2) x.data[0x3000] = 'Z';
        }; });
    Refuse("overlapping external name copies differ", [](Fake& f) {
        Put(f.data, 0x1000 + 0xb0 + 0x90, 0x4000);
        f.on_copy = [](Fake& x, Address a, std::size_t) {
            if (a == 0x4000 && x.counts[a] == 2) x.data[0x3000] = 'Z';
        }; });
    Refuse("copy-refused", [](Fake& f) {
        f.on_copy = [](Fake&, Address, std::size_t) { throw std::runtime_error("copy-refused"); }; });
    Refuse("retained-capture-unknown-failure", [](Fake& f) {
        f.on_copy = [](Fake&, Address, std::size_t) { throw 1; }; });
    std::cout << "RETAINED_CAPTURE_CASES=" << cases
              << " PASS; Adobe_calls=0; callbacks_invoked=0\n";
}
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
void Owned() {
    // Actual mapped reads target only test-owned heap allocations, never AE.
    Bytes records(0xb0, 0); Bytes name{'O', 'w', 'n', 'e', 'd', 0};
    Put(records, 0x90, reinterpret_cast<Address>(name.data())); Put(records, 0x98, 5);
    records[0xa7] = 0x80;
    std::vector<Address> root{reinterpret_cast<Address>(records.data()),
                             reinterpret_cast<Address>(records.data()) + records.size()};
    const auto address = reinterpret_cast<Address>(root.data());
    mapped_memory::SelfBackend backend; Observer o; const auto r = o.run(layout, address, backend);
    Check(r.success && r.identities.at(0).name == Bytes({'O', 'w', 'n', 'e', 'd'}) &&
          r.calls == 8 && r.bytes == 428);
    Observer worker; Diagnostic failed;
    std::thread thread([&] { failed = worker.run(layout, address, backend); }); thread.join();
    Check(!failed.success && failed.failure == "mapped-self-wrong-thread-or-address" &&
          worker.run(layout, address, backend).failure == "retained-capture-consumed");
    std::cout << "OWNED_RETAINED_CAPTURE PASS; foreign_processes=0; Adobe_calls=0\n";
}
#endif
} // namespace
int main() {
    try {
        Synthetic();
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
        Owned();
#endif
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
