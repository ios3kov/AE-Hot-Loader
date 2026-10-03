#include "AEConfig.h"
#include "AE_GeneralPlug.h"
#include "../experiments/ordinary_discovery/ResidentImageBinding.hpp"
#include <cstdlib>
#include <dlfcn.h>
#include <filesystem>
#include <iostream>
namespace {
unsigned acquired=0;
SPErr Acquire(const char*,int32,const void**) { ++acquired;return 1; }
void Need(bool v) { if(!v)throw std::runtime_error("pica-inert-test"); }
}
int main(int argc,char** argv) {
    try {
        Need(argc==4);void* library=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL);Need(library);
        using Entry=A_Err (*)(SPBasicSuite*,A_long,A_long,AEGP_PluginID,AEGP_GlobalRefcon*);
        auto entry=reinterpret_cast<Entry>(dlsym(library,"EntryPointFunc"));Need(entry);
        SPBasicSuite suites{};suites.AcquireSuite=Acquire;
        Need(entry(nullptr,0,0,0,nullptr)==0);
        Need(setenv("AEHL_PICA_AVAILABILITY_TOKEN","wrong-owned-token",1)==0);
        Need(entry(&suites,0,0,0,nullptr)==0);
        Need(setenv("AEHL_PICA_AVAILABILITY_TOKEN",argv[2],1)==0);
        Need(entry(&suites,0,0,0,nullptr)==0&&acquired==0);
        resident_binding::Digest digest{};const std::string hex=argv[3],digits="0123456789abcdef";Need(hex.size()==64);
        for(std::size_t i=0;i<32;++i){const auto a=digits.find(hex[i*2]),b=digits.find(hex[i*2+1]);
            Need(a!=digits.npos&&b!=digits.npos);digest[i]=static_cast<unsigned char>(a*16+b);}
        const auto bound=resident_binding::Resolve({std::filesystem::canonical(argv[1]).string(),digest},{"_AEHL_PicaBuildIdentity"});
        Need(bound.functions.at("_AEHL_PicaBuildIdentity")==dlsym(library,"AEHL_PicaBuildIdentity"));
        digest[0]^=1;bool rejected=false;
        try{(void)resident_binding::Resolve({std::filesystem::canonical(argv[1]).string(),digest},{"_AEHL_PicaBuildIdentity"});}
        catch(...){rejected=true;}Need(rejected);
        std::cout<<"PICA inert/null/token/wrong-host/self-export/changed-hash PASS; SDK providers synthetic; AE NOT RUN\n";
    } catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
