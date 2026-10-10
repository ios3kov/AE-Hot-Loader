// Owned model of byte read -> parsed name -> descriptor copy -> writer -> reader.
// No Adobe headers, binaries, layout assumptions, dynamic loading or debugger.
#include <array>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <map>
#include <memory>
#include <stdexcept>
#include <string>
#include <sstream>
#include <vector>
#include <unistd.h>
#ifdef AEHL_RESOURCE_DEBUGGER
#include <pthread.h>
// Owned wire buffer remains alive and unchanged until this exact NOP returns.
// This is the fixture's contract; no Adobe layout/ownership is inferred.
extern "C" __attribute__((naked, noinline, used)) void resource_probe(
    const char*, std::uint64_t, const char*, std::uint64_t, std::uint64_t) {
    asm volatile(".globl _resource_probe_site\n_resource_probe_site:\nnop\nret\n");
}
#endif

namespace {
std::string run, module, origin, fault;
unsigned sequence = 0;
std::uint64_t id(const void* p) { return reinterpret_cast<std::uintptr_t>(p); }
bool hex(const std::string& s, std::size_t n) {
    return s.size() == n && s.find_first_not_of("0123456789abcdef") == std::string::npos;
}
std::string json_text(const std::string& s) {
    if (s.find_first_not_of("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_:") != std::string::npos)
        throw std::runtime_error("unexpected fixture text");
    return "\"" + s + "\"";
}
std::string number(std::uint64_t n) { return std::to_string(n); }
using Fields = std::vector<std::pair<std::string, std::string>>;
void emit(const std::string& role, const Fields& fields) {
    std::uint64_t thread = 1;
#ifdef AEHL_RESOURCE_DEBUGGER
    if (pthread_threadid_np(nullptr, &thread) != 0) throw std::runtime_error("thread identity");
#endif
    std::ostringstream encoded;
    encoded << "{\"run_id\":" << json_text(run) << ",\"pid\":" << getpid()
              << ",\"thread\":" << thread << ",\"sequence\":" << sequence++
              << ",\"role\":" << json_text(role) << ",\"values\":{";
    bool comma = false;
    for (const auto& field : fields) {
        if (comma) encoded << ',';
        comma = true;
        encoded << json_text(field.first) << ':' << field.second;
    }
    encoded << "}}";
    const std::string wire = encoded.str();
#ifdef AEHL_RESOURCE_DEBUGGER
#ifdef AEHL_RESOURCE_BAD_EXTENT
    resource_probe(wire.data(), 4097, wire.data(), wire.size(), pthread_main_np());
#else
    resource_probe(wire.data(), wire.size(), wire.data(), wire.size(), pthread_main_np());
#endif
#endif
    std::cout << wire << '\n';
}
struct PiPLModel { std::vector<char> bytes; std::string name; };
struct Descriptor { std::array<char, 32> name{}; std::shared_ptr<int> routine; };
struct Registry {
    std::vector<std::shared_ptr<Descriptor>> records;
    std::map<std::string, std::shared_ptr<Descriptor>> names;
};
void reader_probe() {}
}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 6) return 2;
        run = argv[2]; module = argv[3]; origin = argv[4]; fault = argv[5];
        if (!hex(run, 32) || !hex(module, 64) ||
            (origin != "bundle-resource" && origin != "legacy-resource" && origin != "cache") ||
            (fault != "none" && fault != "alias" && fault != "writer-failure" && fault != "wrong-owner" && fault != "read-name")) return 2;
        std::ifstream file(argv[1], std::ios::binary);
        std::vector<char> bytes;
        for (char c; file.get(c);) {
            if (bytes.size() == 128) throw std::runtime_error("byte budget");
            bytes.push_back(c);
        }
        if (!file.eof() || bytes.size() != 23 || std::string(bytes.data(), 5) != "eMNA:" || bytes.back() != '\0') return 2;
        const std::string name(bytes.data() + 5, bytes.size() - 6);
        if (name.substr(0, 5) != "AEHLR" || !hex(name.substr(5), 12)) return 2;
        std::string encoded;
        const char* alphabet = "0123456789abcdef";
        for (unsigned char c : bytes) { encoded += alphabet[c >> 4]; encoded += alphabet[c & 15]; }
        const auto call = id(&file);
        emit("producer", {{"call",number(call)}, {"origin",json_text(origin)},
             {"module_sha256",json_text(module)}, {"payload_hex",json_text(encoded)}});
        auto pipl = std::make_shared<PiPLModel>(); pipl->bytes = bytes; pipl->name = name;
        const auto p = id(pipl.get()), po = id(&pipl), source = id(pipl->name.c_str());
        emit("pipl", {{"call",number(call)}, {"pipl",number(p)}, {"pipl_owner",number(po)},
             {"source_storage",number(source)}, {"name",json_text(pipl->name)}});
        emit("getter", {{"call",number(call)}, {"pipl",number(p)}, {"source_storage",number(source)}, {"name",json_text(pipl->name)}});
        auto descriptor = std::make_shared<Descriptor>(); descriptor->routine = std::make_shared<int>(17);
        std::memcpy(descriptor->name.data(), pipl->name.c_str(), pipl->name.size() + 1);
        const auto d = id(descriptor.get()), owner = id(&descriptor), routine = id(descriptor->routine.get());
        const auto target = id(descriptor->name.data());
        emit("copy", {{"call",number(call)}, {"pipl",number(p)}, {"descriptor",number(d)},
             {"descriptor_owner",number(owner)}, {"routine_owner",number(routine)},
             {"source_storage",number(source)}, {"target_storage",number(fault == "alias" ? source : target)}, {"name",json_text(descriptor->name.data())}});
        Registry registry; const auto root = id(&registry);
        emit("writer", {{"descriptor",number(d)}, {"descriptor_owner",number(owner)}, {"routine_owner",number(routine)},
             {"root",number(root)}, {"target_storage",number(target)}, {"name",json_text(descriptor->name.data())}});
        registry.records.push_back(descriptor); registry.names.emplace(descriptor->name.data(), descriptor);
        emit("index", {{"descriptor",number(id(registry.records.at(0).get()))}, {"root",number(root)}, {"index","0"}});
        emit("writer_return", {{"root",number(root)}, {"status",fault == "writer-failure" ? "1" : "0"}});
        const auto function = id(reinterpret_cast<const void*>(&reader_probe));
        emit("reader_start", {{"key","703"}, {"function",number(function)}});
        auto retained = registry.records.at(0);
        if (registry.names.at(name).get() != retained.get()) return 2;
        emit("lookup", {{"descriptor",number(id(retained.get()))},
             // The fixture token denotes its initial owner, NOT a Boost ABI/control block.
             {"descriptor_owner",number(fault == "wrong-owner" ? owner + 1 : owner)},
             {"routine_owner",number(id(retained->routine.get()))}, {"root",number(root)}, {"index","1"}});
        std::array<char,32> output{};
        std::memcpy(output.data(), retained->name.data(), output.size());
        if (fault == "read-name") output[0] = 'X';
        emit("reader_return", {{"key","703"}, {"function",number(function)}, {"status","0"},
             {"output_storage",number(id(output.data()))}, {"name",json_text(output.data())}});
        return 0;
    } catch (...) { return 2; }
}
