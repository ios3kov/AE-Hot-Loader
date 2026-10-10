// Initialized OWNED storage only. This is not an AE capture/initializer contract.
#include <CoreFoundation/CoreFoundation.h>
#include <CoreServices/CoreServices.h>
#include <array>
#include <cstring>
#include <cstdint>
#include <dlfcn.h>
#include <iomanip>
#include <iostream>
#include <mach-o/dyld.h>
#include <mach-o/loader.h>
#include <new>
#include <sstream>
#include <stdexcept>
#include <unistd.h>

#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wdeprecated-declarations"
namespace {
struct Url {
    CFURLRef value;
    explicit Url(const char* path):value(CFURLCreateFromFileSystemRepresentation(
        nullptr,reinterpret_cast<const UInt8*>(path),std::strlen(path),false)) {
        if(!value) throw std::runtime_error("URL_CREATE");
    }
    ~Url(){CFRelease(value);}
    Url(const Url&)=delete; Url& operator=(const Url&)=delete;
};
std::string hex(const void* data,std::size_t count) {
    const auto* bytes=static_cast<const unsigned char*>(data);
    std::ostringstream out;
    out << std::hex << std::setfill('0');
    for(std::size_t i=0;i<count;++i) out << std::setw(2) << unsigned(bytes[i]);
    return out.str();
}
// dyld owns these mapped headers; no disk image hash is claimed for shared-cache code.
std::string image(const void* function) {
    Dl_info info{};
    if(!dladdr(function,&info) || !info.dli_fname || !info.dli_fbase)
        throw std::runtime_error("IMAGE_IDENTITY");
    std::string uuid;
    for(std::uint32_t i=0;i<_dyld_image_count();++i) {
        const auto* header=_dyld_get_image_header(i);
        if(reinterpret_cast<const void*>(header)!=info.dli_fbase) continue;
        if(header->magic!=MH_MAGIC_64) throw std::runtime_error("IMAGE_ABI");
        const auto* begin=reinterpret_cast<const unsigned char*>(header)+sizeof(mach_header_64);
        std::size_t used=0;
        for(std::uint32_t n=0;n<header->ncmds;++n) {
            if(used>header->sizeofcmds || header->sizeofcmds-used<sizeof(load_command))
                throw std::runtime_error("IMAGE_COMMAND");
            const auto* command=reinterpret_cast<const load_command*>(begin+used);
            if(command->cmdsize<sizeof(load_command) || command->cmdsize>header->sizeofcmds-used)
                throw std::runtime_error("IMAGE_COMMAND");
            if(command->cmd==LC_UUID) {
                if(command->cmdsize!=sizeof(uuid_command) || !uuid.empty())
                    throw std::runtime_error("IMAGE_UUID");
                uuid=hex(reinterpret_cast<const uuid_command*>(command)->uuid,16);
            }
            used+=command->cmdsize;
        }
        break;
    }
    if(uuid.size()!=32) throw std::runtime_error("IMAGE_UUID");
    // JSON-safe fixed system paths required rather than emitting an unescaped path.
    const std::string path=info.dli_fname;
    if(path.find_first_of("\"\\\n\r\t")!=std::string::npos) throw std::runtime_error("IMAGE_PATH");
    return "{\"path\":\""+path+"\",\"uuid\":\""+uuid+"\"}";
}
FSRef expected(CFURLRef url) {
    FSRef result{};
    if(!CFURLGetFSRef(url,&result)) throw std::runtime_error("EXPECTED_REF");
    return result;
}
using Bytes=std::array<unsigned char,80>;
Bytes pattern(unsigned index) {
    Bytes result{}; std::uint32_t state=index==3 ? 0x12345678u : 0x98765432u;
    for(std::size_t i=0;i<result.size();++i) {
        if(index==0) result[i]=0;
        else if(index==1) result[i]=0xa5;
        else if(index==2) result[i]=(i%2)?0xaa:0x55;
        else {state^=state<<13; state^=state>>17; state^=state<<5; result[i]=state&255;}
    }
    return result;
}
struct alignas(16) Storage {std::array<unsigned char,128> bytes;};
void row(unsigned id,const char* kind,unsigned alignment,unsigned repeat,unsigned prefill,
         unsigned generation,Storage& storage,CFURLRef url,const Bytes& before,
         const FSRef& a,const FSRef& b) {
    storage.bytes.fill(0xcc);
    const std::size_t offset=16+alignment;
    auto* ref=new(storage.bytes.data()+offset) FSRef; // Lifetime begins before the complete own prefill.
    std::memcpy(ref,before.data(),sizeof(FSRef));
    const Boolean ready=CFURLGetFSRef(url,ref);
    Bytes after{}; std::memcpy(after.data(),ref,after.size());
    bool guard=true;
    for(std::size_t i=0;i<storage.bytes.size();++i)
        if((i<offset || i>=offset+80) && storage.bytes[i]!=0xcc) guard=false;
    std::cout << "{\"id\":" << id << ",\"kind\":\"" << kind << "\",\"alignment\":" << alignment
        << ",\"repeat\":" << repeat << ",\"prefill\":" << prefill << ",\"generation\":" << generation
        << ",\"pointer\":" << reinterpret_cast<std::uintptr_t>(ref)
        << ",\"ready\":" << (ready?"true":"false") << ",\"guards\":" << (guard?"true":"false")
        << ",\"before\":\"" << hex(before.data(),80) << "\",\"after\":\"" << hex(after.data(),80) << "\"";
    if(ready) {
        const OSErr ca=FSCompareFSRefs(ref,&a),cb=FSCompareFSRefs(ref,&b);
        if((ca!=noErr && ca!=errFSRefsDifferent) || (cb!=noErr && cb!=errFSRefsDifferent))
            throw std::runtime_error("COMPARE_INCONCLUSIVE");
        std::cout << ",\"compare_a\":" << ca << ",\"compare_b\":" << cb;
    } else std::cout << ",\"compare_a\":null,\"compare_b\":null";
    std::cout << "}";
    ref->~FSRef();
}
}
int main(int argc,char** argv) {
    static_assert(sizeof(FSRef)==80 && alignof(FSRef)==1,"FSRef target ABI");
    try {
        if(argc==5 && std::string(argv[1])=="compare_AB") {
            // One independently initialized process, A first then B.
            Url ua(argv[2]),ub(argv[3]); FSRef a{},b{};
            const std::string order=argv[4];
            if(order=="AB") {a=expected(ua.value); b=expected(ub.value);}
            else if(order=="BA") {b=expected(ub.value); a=expected(ua.value);}
            else throw std::runtime_error("ORDER");
            FSRef captured{};
            std::cin.read(reinterpret_cast<char*>(&captured),80);
            if(std::cin.gcount()!=80 || std::cin.peek()!=std::char_traits<char>::eof())
                throw std::runtime_error("WIRE_LENGTH");
            const OSErr ca=FSCompareFSRefs(&captured,&a),cb=FSCompareFSRefs(&captured,&b);
            std::cout << "{\"pid\":" << getpid() << ",\"order\":\"" << order
                << "\",\"compare_a\":" << ca << ",\"compare_b\":" << cb
                << ",\"images\":{\"initializer\":" << image(reinterpret_cast<const void*>(&CFURLGetFSRef))
                << ",\"comparator\":" << image(reinterpret_cast<const void*>(&FSCompareFSRefs)) << "}}\n";
            return 0;
        }
        if(argc!=4) throw std::runtime_error("ARGUMENTS");
        Url ua(argv[1]),ub(argv[2]),missing(argv[3]);
        const FSRef a=expected(ua.value),b=expected(ub.value);
        if(FSCompareFSRefs(&a,&b)!=errFSRefsDifferent) throw std::runtime_error("TWIN_IDENTITY");
        std::cout << "{\"pid\":" << getpid() << ",\"images\":{\"initializer\":"
            << image(reinterpret_cast<const void*>(&CFURLGetFSRef)) << ",\"comparator\":"
            << image(reinterpret_cast<const void*>(&FSCompareFSRefs)) << "},\"rows\":[";
        unsigned id=0;
        Storage storage{};
        for(unsigned alignment: {0u,8u}) for(unsigned repeat=0;repeat<2;++repeat)
            for(unsigned fill=0;fill<5;++fill) for(unsigned file=0;file<2;++file) {
                if(id) std::cout << ',';
                row(id,file?"B":"A",alignment,repeat,fill,id+1,storage,
                    file?ub.value:ua.value,pattern(fill),a,b); ++id;
            }
        // A real sequence at the same owned address; generation is wrapper metadata, not AE inference.
        Bytes known_a{};std::memcpy(known_a.data(),&a,80);
        for(unsigned step=0;step<4;++step) {
            std::cout << ',';
            row(id,step==2?"missing":"reuse_A",8,step,5,id+1,storage,
                step==2?missing.value:ua.value,known_a,a,b); ++id;
        }
        std::cout << "]}\n";
        return 0;
    } catch(const std::exception& error){std::cerr << error.what() << '\n';return 2;}
}
#pragma clang diagnostic pop
