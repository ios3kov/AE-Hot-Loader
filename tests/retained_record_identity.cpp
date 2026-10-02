#include "../experiments/ordinary_discovery/RetainedRecordIdentity.hpp"

#include <algorithm>
#include <iostream>
#include <string>

using namespace retained_identity;
namespace {
std::size_t cases = 0;
void Check(bool condition, const char* reason) {
    if (!condition) throw std::runtime_error(reason);
}
void Put(Bytes& bytes, std::size_t offset, Address value) {
    for (std::size_t i = 0; i < 8; ++i)
        bytes.at(offset + i) = static_cast<unsigned char>(value >> (8 * i));
}
Bytes Inline(const Bytes& name) {
    Bytes bytes(kStride, 0);
    Check(name.size() <= 22, "fixture inline size");
    std::copy(name.begin(), name.end(), bytes.begin() + 0x90);
    bytes[0xa7] = static_cast<unsigned char>(name.size());
    return bytes;
}
Bytes External(Address address, Address length) {
    Bytes bytes(kStride, 0);
    Put(bytes, 0x90, address);
    Put(bytes, 0x98, length);
    bytes[0xa7] = 0x80;
    return bytes;
}
void Append(Bytes& records, const Bytes& record) {
    records.insert(records.end(), record.begin(), record.end());
}
template<class F> void Pass(F test) { test(); ++cases; }
template<class F> void Refuse(const char* reason, F test) {
    bool refused = false;
    try { test(); } catch (const std::runtime_error& error) {
        Check(std::string(error.what()) == reason, "wrong refusal reason");
        refused = true;
    }
    Check(refused, "accepted invalid input");
    ++cases;
}
constexpr auto layout = Layout::Mee256Arm64;
} // namespace

int main() {
    try {
        Pass([] { Check(Decode(layout, {}, 0, {}).empty(), "empty inventory"); });
        Pass([] {
            auto bytes = Inline({'A', 0xff, 0, 'Z'});
            Put(bytes, 0, 0x1122334455667788);
            Put(bytes, 8, 0x8877665544332211);
            Put(bytes, 0x10, 0x1020304050607080);
            Put(bytes, 0x58, 0xffeeddccbbaa9988);
            Put(bytes, 0x80, 0x9988776655443322);
            bytes[0xa8] = 0xff;
            const auto record = Decode(layout, bytes, 1, {}).at(0);
            Check(record.descriptor == 0x1122334455667788 &&
                  record.control == 0x8877665544332211 &&
                  record.opaque_state == 0x1020304050607080 &&
                  record.teardown == 0xffeeddccbbaa9988 &&
                  record.finish == 0x9988776655443322 && record.marker == 0xff &&
                  !record.external_name && record.name == Bytes({'A', 0xff, 0, 'Z'}),
                  "raw identity fields");
        });
        Pass([] { Check(Decode(layout, Inline(Bytes(22, 'x')), 1, {}).at(0).name.size()
                        == 22, "maximum inline name"); });
        Pass([] { Check(Decode(layout, Inline({}), 1, {}).at(0).name.empty(),
                        "empty inline name"); });
        Pass([] {
            auto records = External(0x1000, 255);
            auto payload = Bytes(256, 'x'); payload.back() = 0;
            const auto plan = Plan(layout, records, 1);
            Check(plan.size() == 1 && plan[0].index == 0 &&
                  plan[0].address == 0x1000 && plan[0].size == 256, "copy plan");
            Check(Decode(layout, records, 1, {{0, 0x1000, payload}}).at(0).name.size()
                  == 255, "maximum external name");
        });
        Pass([] { Check(Decode(layout, External(1, 0), 1, {{0, 1, {0}}}).at(0)
                        .name.empty(), "empty allocated name"); });
        Pass([] {
            Bytes records;
            for (std::size_t i = 0; i < 8; ++i) Append(records, Inline({'A'}));
            const auto decoded = Decode(layout, records, 8, {});
            Check(decoded.size() == 8 && decoded[0].name == decoded[7].name,
                  "preserve duplicate maximum inventory");
        });
        Pass([] {
            auto records = External(0x1000, 1);
            Append(records, Inline({'B'})); Append(records, External(0x2000, 1));
            const auto decoded = Decode(layout, records, 3,
                {{2, 0x2000, {'C', 0}}, {0, 0x1000, {'A', 0}}});
            Check(decoded[0].name == Bytes({'A'}) && decoded[1].name == Bytes({'B'})
                  && decoded[2].name == Bytes({'C'}), "order with reversed copies");
        });
        Pass([] {
            auto records = External(0x1000, 1);
            Append(records, External(0x1000, 1));
            Check(Decode(layout, records, 2, {{0, 0x1000, {'A', 0}},
                    {1, 0x1000, {'A', 0}}}).size() == 2, "alias preserves records");
        });
        Pass([] {
            auto records = External(0x1000, 2);
            Append(records, External(0x1001, 1));
            Check(Decode(layout, records, 2, {{0, 0x1000, {'A', 'B', 0}},
                    {1, 0x1001, {'B', 0}}}).size() == 2, "consistent overlap");
        });
        Pass([] {
            auto records = External(1, 1);
            records[0xa7] = 0xff;
            Check(Decode(layout, records, 1, {{0, 1, {0xff, 0}}}).at(0).name
                  == Bytes({0xff}), "opaque capacity and encoding");
        });
        Pass([] {
            auto records = External(0x1000, 1);
            const auto original = records;
            std::vector<NameCopy> copies{{0, 0x1000, {'A', 0}}};
            auto decoded = Decode(layout, records, 1, copies);
            copies[0].bytes[0] = 'Z'; records[0] = 0xff;
            Check(decoded[0].name == Bytes({'A'}) && original[0] == 0,
                  "result owns bytes");
        });
        Refuse("unsupported layout", [] { Plan(static_cast<Layout>(0), {}, 0); });
        Refuse("record count limit", [] { Plan(layout, {}, 9); });
        Refuse("record count limit", [] {
            Plan(layout, {}, std::numeric_limits<std::size_t>::max()); });
        Refuse("record payload size", [] { Plan(layout, Bytes(kStride - 1), 1); });
        Refuse("record payload size", [] { Plan(layout, Bytes(kStride + 1), 1); });
        Refuse("record payload size", [] { Plan(layout, Bytes(kStride), 0); });
        Refuse("inline name length", [] {
            auto bytes = Inline({}); bytes[0xa7] = 23; Plan(layout, bytes, 1); });
        Refuse("inline name length", [] {
            auto bytes = Inline({}); bytes[0xa7] = 127; Plan(layout, bytes, 1); });
        Refuse("inline name terminator", [] {
            auto bytes = Inline({'A'}); bytes[0x91] = 'x'; Plan(layout, bytes, 1); });
        Refuse("external name length limit", [] { Plan(layout, External(1, 256), 1); });
        Refuse("external name length limit", [] {
            Plan(layout, External(1, std::numeric_limits<Address>::max()), 1); });
        Refuse("external name address", [] { Plan(layout, External(0, 1), 1); });
        Refuse("external name range overflow", [] {
            Plan(layout, External(std::numeric_limits<Address>::max(), 0), 1); });
        Refuse("external name inventory", [] {
            Decode(layout, External(1, 1), 1, {}); });
        Refuse("external name inventory", [] {
            Decode(layout, Inline({'A'}), 1, {{0, 1, {'A', 0}}}); });
        Refuse("external name index", [] {
            Decode(layout, External(1, 1), 1, {{1, 1, {'A', 0}}}); });
        Refuse("duplicate external name copy", [] {
            auto records = External(1, 1); Append(records, External(2, 1));
            Decode(layout, records, 2, {{0, 1, {'A', 0}}, {0, 1, {'A', 0}}}); });
        Refuse("missing external name copy", [] {
            auto records = External(1, 1); Append(records, Inline({'B'}));
            Decode(layout, records, 2, {{1, 1, {'A', 0}}}); });
        Refuse("external name address mismatch", [] {
            Decode(layout, External(1, 1), 1, {{0, 2, {'A', 0}}}); });
        Refuse("external name payload size", [] {
            Decode(layout, External(1, 1), 1, {{0, 1, {}}}); });
        Refuse("external name payload size", [] {
            Decode(layout, External(1, 1), 1, {{0, 1, {'A'}}}); });
        Refuse("external name payload size", [] {
            Decode(layout, External(1, 1), 1, {{0, 1, {'A', 0, 0}}}); });
        Refuse("external name terminator", [] {
            Decode(layout, External(1, 1), 1, {{0, 1, {'A', 'x'}}}); });
        Refuse("overlapping external name copies differ", [] {
            auto records = External(1, 1); Append(records, External(1, 1));
            Decode(layout, records, 2, {{0, 1, {'A', 0}}, {1, 1, {'B', 0}}}); });
        Refuse("overlapping external name copies differ", [] {
            auto records = External(1, 2); Append(records, External(2, 1));
            Decode(layout, records, 2, {{0, 1, {'A', 'B', 0}}, {1, 2, {'C', 0}}}); });
        Refuse("overlapping external name copies differ", [] {
            auto records = External(1, 1); Append(records, External(2, 1));
            Decode(layout, records, 2, {{0, 1, {'A', 0}}, {1, 2, {'C', 0}}}); });
        std::cout << "RETAINED_IDENTITY_CASES=" << cases
                  << " PASS; host_calls=0; record_calls=0\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n'; return 1;
    }
}
