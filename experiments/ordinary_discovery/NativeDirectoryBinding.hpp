// Research-only concrete binding seam; no entrypoint, auto-run or scan operation.
// A profile MUST come from the reviewed immutable build, never request data.
// Actual U/dvacore implementation review and their pins are still outstanding.
#pragma once
#include "DirectorySpecAdapter.hpp"
#include "ResidentImageBinding.hpp"
namespace native_directory {
inline const std::vector<std::string>& FileExports() {
    static const std::vector<std::string> names{
        "__Z8FILE_NewRKNSt3__112basic_stringItNS_11char_traitsItEEN7dvacore9allocator12STLAllocatorItEEEE",
        "__Z10FILE_IsDirPK9FILE_Spec", "__Z19FILE_InqUnicodePathPK9FILE_Spec", "_FILE_Dispose"};
    return names;
}
inline const std::string& ProducerExport() {
    static const std::string name = "__Z20U_AsciiToUTF16StringPKc"; return name;
}
inline const std::string& DestructorExport() {
    static const std::string name = "__ZNSt3__112basic_stringItNS_11char_traitsItEEN7dvacore9allocator12STLAllocatorItEEED1Ev";
    return name;
}
#if defined(__APPLE__) && defined(__aarch64__) && !defined(__arm64e__)
extern "C" void AEHL_Arm64_IndirectResult(const void*, const void*, void*);
struct Profile { std::string frameworks; resident_binding::Digest file{}, utility{}, core{}; };
inline directory_spec::Functions Bind(const Profile& profile) {
    using namespace resident_binding;
    Require(Path(profile.frameworks) && profile.frameworks.size() > 20);
    const std::string suffix = ".app/Contents/Frameworks";
    Require(profile.frameworks.size() >= suffix.size() &&
            profile.frameworks.compare(profile.frameworks.size() - suffix.size(), suffix.size(), suffix) == 0);
    for (const auto& digest : {profile.file, profile.utility, profile.core})
        Require(std::any_of(digest.begin(), digest.end(), [](unsigned char c) { return c; }));
    const auto before = Snapshot();
    const auto file = Resolve({profile.frameworks + "/FILE.dylib", profile.file}, FileExports());
    const auto utility = Resolve({profile.frameworks + "/U.dylib", profile.utility}, {ProducerExport()});
    const auto core = Resolve({profile.frameworks + "/dvacore.framework/Versions/A/dvacore", profile.core}, {DestructorExport()});
    Require(before == Snapshot());
    directory_spec::Functions f;
    f.indirect = AEHL_Arm64_IndirectResult;
    f.ascii_to_host = utility.functions.at(ProducerExport());
    f.inquire_path = file.functions.at(FileExports()[2]);
    f.destroy_string = reinterpret_cast<decltype(f.destroy_string)>(core.functions.at(DestructorExport()));
    f.new_spec = reinterpret_cast<decltype(f.new_spec)>(file.functions.at(FileExports()[0]));
    f.is_dir = reinterpret_cast<decltype(f.is_dir)>(file.functions.at(FileExports()[1]));
    f.dispose_spec = reinterpret_cast<decltype(f.dispose_spec)>(file.functions.at(FileExports()[3]));
    f.read_memory = directory_spec::ReadSelfMemory;
    Require(f.complete()); return f;
    // Resolved addresses are not an authorization, ABI proof or lifetime lease.
    // No AE caller exists. The future claimed/supervised probe must check current
    // host/project/root state and must NOT cache this table across requests.
}
#endif
} // namespace native_directory
