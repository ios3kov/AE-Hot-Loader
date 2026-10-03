#pragma once
#include "PicaAvailability.hpp"
namespace pica_probe {
struct Config { std::string run, source, build, executable, module, control, token, host_sha256; };
inline bool HexValue(const std::string& text, std::size_t n) {
    return text.size() == n && text.find_first_not_of("0123456789abcdef") == std::string::npos;
}
inline std::string Request(const Config& c, std::uint64_t pid, const std::string& start,
                           const std::string& binary) {
    if (!HexValue(c.source,40) || !HexValue(c.token,32) || !HexValue(binary,64) ||
        c.run.empty() || c.build.empty() || c.run.find('\n')!=c.run.npos ||
        c.build.find('\n')!=c.build.npos || !pid || start.empty() || start.size()>32 ||
        start.find_first_not_of("0123456789.")!=start.npos)
        throw std::runtime_error("request-config");
    return "schema=PICA-REQUEST-1\nkind=pica-availability\nrun="+c.run+"\nsource="+c.source+
        "\nbuild="+c.build+"\npid="+std::to_string(pid)+"\nstart="+start+"\ntoken="+c.token+
        "\nbinary_sha256="+binary+"\npotential_suite_load=authorized\nadapter_enumeration=authorized\n";
}
inline std::string Approve(const Config& c, std::uint64_t pid, const std::string& start,
                           const std::string& bytes) {
    const auto prefix = Request(c,pid,start,std::string(64,'0'));
    const auto at = prefix.find("binary_sha256=")+14;
    if(bytes.size()!=prefix.size())throw std::runtime_error("request-size");
    const auto sha=bytes.substr(at,64);
    if(bytes!=Request(c,pid,start,sha))throw std::runtime_error("request-identity");
    return sha; // Exact transport binding; loaded self hash is still independently checked.
}
} // namespace pica_probe
