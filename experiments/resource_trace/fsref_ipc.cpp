// Own-file Carbon control. This instrumented program is not an Adobe ABI model.
#include <CoreFoundation/CoreFoundation.h>
#include <CoreServices/CoreServices.h>
#include <array>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <memory>
#include <pthread.h>
#include <stdexcept>
#include <unistd.h>
#include <vector>

#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wdeprecated-declarations"
extern "C" __attribute__((naked, noinline, used)) void fsref_probe(
    std::uint64_t, std::uint64_t, std::uint64_t, const void*, std::uint64_t,
    std::uint64_t, std::uint64_t, std::uint64_t) {
    asm volatile(".globl _fsref_probe_site\n_fsref_probe_site:\nnop\nret\n");
}
namespace {
struct Url {
    CFURLRef value;
    explicit Url(const char* path): value(CFURLCreateFromFileSystemRepresentation(
        nullptr,reinterpret_cast<const UInt8*>(path),std::strlen(path),false)) {
        if(!value) throw std::runtime_error("URL_CREATE_FAILED");
    }
    ~Url() { CFRelease(value); }
    Url(const Url&)=delete; Url& operator=(const Url&)=delete;
};
FSRef reference(const char* path) {
    Url url(path); FSRef result{};
    if(!CFURLGetFSRef(url.value,&result)) throw std::runtime_error("FSREF_CREATE_FAILED");
    return result;
}
unsigned sequence=0;
void event(unsigned phase, unsigned invocation, unsigned parent, const void* data=nullptr,
           std::uint64_t size=0, std::uint64_t status=0) {
    fsref_probe(phase,invocation,parent,data,size,status,pthread_main_np(),sequence++);
}
struct Fork {
    FSIORefNum value=0; bool open=false;
    ~Fork() { if(open) FSCloseFork(value); }
    void close() {
        if(!open || FSCloseFork(value)!=noErr) throw std::runtime_error("FORK_CLOSE_FAILED");
        open=false;
    }
};
void produce(const char* path, const char* twin, unsigned invocation, unsigned parent,
             bool nested, bool unwind) {
    event(1,invocation,parent);
    Url url(path); FSRef ref{}; // All80bytes initialized by our own declaration.
    const Boolean ready=CFURLGetFSRef(url.value,&ref);
    event(2,invocation,parent,&ref,sizeof(ref),ready);
    if(!ready) throw std::runtime_error("FSREF_CREATE_FAILED");
    if(nested) produce(twin,path,2,invocation,false,false);
    HFSUniStr255 fork_name{};
    if(FSGetDataForkName(&fork_name)!=noErr) throw std::runtime_error("FORK_NAME_FAILED");
    Fork fork;
    const OSErr opened=FSOpenFork(&ref,fork_name.length,fork_name.unicode,fsRdPerm,&fork.value);
    fork.open=opened==noErr;
    event(3,invocation,parent,&fork.value,sizeof(fork.value),static_cast<std::uint16_t>(opened));
    if(!fork.open) throw std::runtime_error("FORK_OPEN_FAILED");
    SInt64 size=0; const OSErr sized=FSGetForkSize(fork.value,&size);
    event(4,invocation,parent,&size,sizeof(size),static_cast<std::uint16_t>(sized));
    if(sized!=noErr || size<=0 || size>4096) throw std::runtime_error("FORK_SIZE_REFUSED");
    auto allocation=std::make_unique<unsigned char[]>(static_cast<std::size_t>(size));
    event(5,invocation,parent,allocation.get(),static_cast<std::uint64_t>(size));
    if(unwind) {
        // Real C++ exception/RAII cleanup; no normal read/copy events may follow.
        throw std::runtime_error("OWNED_UNWIND");
    }
    ByteCount actual=0;
    const OSErr read=FSReadFork(fork.value,fsFromStart,0,static_cast<ByteCount>(size),allocation.get(),&actual);
    // Initialized own wire output connects this actual read to its input tokens.
    const std::array<std::uint64_t,3> read_output{{reinterpret_cast<std::uintptr_t>(allocation.get()),
        actual,static_cast<std::uint32_t>(fork.value)}};
    event(6,invocation,parent,read_output.data(),sizeof(read_output),static_cast<std::uint16_t>(read));
    if(read!=noErr || actual!=static_cast<ByteCount>(size)) throw std::runtime_error("FORK_READ_FAILED");
    std::vector<unsigned char> copy(static_cast<std::size_t>(actual));
    std::memcpy(copy.data(),allocation.get(),static_cast<std::size_t>(actual));
    event(7,invocation,parent,copy.data(),actual);
    fork.close();
    // Pointer identity at release; the observer must not read these bytes here.
    event(8,invocation,parent,allocation.get(),0);
    allocation.reset();
    event(9,invocation,parent);
}
}
int main(int argc,char** argv) {
    static_assert(sizeof(FSRef)==80 && sizeof(FSIORefNum)==4 && sizeof(ByteCount)==8,"target ABI");
    try {
        if(argc!=4) throw std::runtime_error("ARGUMENTS");
        const std::string mode=argv[1];
        if(mode=="emit") {
            const FSRef first=reference(argv[2]), second=reference(argv[3]);
            std::cout.write(reinterpret_cast<const char*>(&first),sizeof(first));
            std::cout.write(reinterpret_cast<const char*>(&second),sizeof(second));
            std::cerr << "{\"pid\":" << getpid() << ",\"bytes\":160}\n";
        } else if(mode=="compare") {
            const FSRef expected=reference(argv[2]); FSRef captured{};
            std::cin.read(reinterpret_cast<char*>(&captured),sizeof(captured));
            if(std::cin.gcount()!=sizeof(captured) || std::cin.peek()!=std::char_traits<char>::eof())
                throw std::runtime_error("FSREF_WIRE_LENGTH");
            const OSErr result=FSCompareFSRefs(&expected,&captured);
            if(result!=noErr && result!=errFSRefsDifferent) throw std::runtime_error("FSREF_COMPARE_INCONCLUSIVE");
            std::cout << "{\"pid\":" << getpid() << ",\"status\":" << result
                      << ",\"same\":" << (result==noErr?"true":"false") << "}\n";
        } else if(mode=="nested" || mode=="unwind") {
            try { produce(argv[2],argv[3],1,0,mode=="nested",mode=="unwind"); }
            catch(const std::runtime_error& error) {
                if(mode!="unwind" || std::string(error.what())!="OWNED_UNWIND") throw;
                event(11,1,0); // The scoped ref/allocation are already destroyed.
            }
            event(10,0,0);
            std::cout << "{\"pid\":" << getpid() << ",\"status\":\"OWNED_COMPLETE\"}\n";
        } else throw std::runtime_error("MODE");
        return 0;
    } catch(const std::exception& error) { std::cerr << error.what() << '\n'; return 2; }
}
#pragma clang diagnostic pop
