#pragma once
#include "PicaInventory.hpp"
#include "PicaProbeContract.hpp"
namespace pica_inventory {
using pica_probe::Config;
using pica_probe::HexValue;
struct Known {std::string bundle,module,sha,resource,resource_sha,match;};
inline std::string Request(const Config& c,std::uint64_t pid,const std::string& start,const std::string& sha) {
    auto body=pica_probe::Request(c,pid,start,sha);
    const auto at=body.find("kind=pica-availability");
    body.replace(at,std::string("kind=pica-availability").size(),"kind=pica-inventory");
    const auto scope=body.find("adapter_enumeration=authorized");
    body.replace(scope,std::string("adapter_enumeration=authorized").size(),"plugin_inventory=authorized");
    return body;
}
inline std::string Approve(const Config& c,std::uint64_t pid,const std::string& start,const std::string& bytes) {
    const auto template_bytes=pica_inventory::Request(c,pid,start,std::string(64,'0'));
    if(bytes.size()!=template_bytes.size())throw std::runtime_error("inventory-request-size");
    const auto sha=bytes.substr(template_bytes.find("binary_sha256=")+14,64);
    if(bytes!=pica_inventory::Request(c,pid,start,sha))throw std::runtime_error("inventory-request-identity");return sha;
}
} // namespace pica_inventory
