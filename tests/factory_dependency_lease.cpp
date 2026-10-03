#include "../experiments/ordinary_discovery/OwnedFactoryDependencyLease.hpp"
#include "../experiments/ordinary_discovery/AE256FactoryReferenceIdentityProfile.hpp"
#include <fstream>
#include <iterator>
#include <iostream>
#include <thread>
#include <cstdio>
#include <sys/resource.h>
using namespace owned_factory_dependency;
static std::vector<int> events;
static void (*callbacks[2])() noexcept = {};
static bool unloaded[2]{};
static Lease* reentry_target=nullptr;
static bool reentry_move=false;
static void Event(int n) noexcept {
    events.push_back(n); if(n==31) unloaded[0]=true; if(n==41) unloaded[1]=true;
    if(n==30&&reentry_target) {
        if(reentry_move){auto moved=std::move(*reentry_target);(void)moved;}
        bool blocked=false;try{(void)reentry_target->Diagnostic();}catch(const std::exception&){blocked=true;}
        if(!blocked){std::fputs("diagnostic-during-factory-cleanup-not-refused\n",stderr);std::_Exit(89);}
        reentry_target->Reset(); // active cleanup must remain idempotent
    }
}
static void SafeTeardown() noexcept {
    // Detect the wrong order BEFORE dispatch through an expired code address.
    if(unloaded[0] || unloaded[1]) { std::fputs("dependency-unloaded-before-factory-cleanup\n",stderr);std::_Exit(85); }
    callbacks[0]();callbacks[1]();
}
template<class T> static T Symbol(void* h,const char* name) { auto p=dlsym(h,name);Require(p);return reinterpret_cast<T>(p); }
template<class F> static void Refuse(F f) { bool denied=false;try{f();}catch(const std::exception&){denied=true;}Require(denied); }
static Profile Make(char** argv,const char* anchor,const char* first,const char* second) {
    std::ifstream f(argv[0],std::ios::binary);Require(bool(f));Bytes b(std::istreambuf_iterator<char>(f),{});
    std::vector<Entry> entries{{first,std::stoull(argv[1],nullptr,0),std::stoull(argv[2],nullptr,0)},
                               {second,std::stoull(argv[3],nullptr,0),std::stoull(argv[4],nullptr,0)}};
    std::sort(entries.begin(),entries.end(),[](const Entry&a,const Entry&b){return a.vm<b.vm;});
    auto layout=Describe(b,anchor,entries);Profile p{{argv[0],Hash(b)},anchor,layout.image.uuid,{}};
    for(const auto&e:entries)p.spans.push_back({e,Hash(SpanBytes(b,layout,e.tag))});return p;
}
int main(int argc,char**argv) {
    try {
        Require(argc==17);const rlimit core_limit{0,0};Require(setrlimit(RLIMIT_CORE,&core_limit)==0);events.reserve(128);
        auto factory=Make(argv+1,classref_call_lease::Anchor,"acquire","destroy");
        std::vector<Profile> deps{Make(argv+6,Anchor,"version","teardown"),Make(argv+11,Anchor,"version","teardown")};
        const auto snapshot=Snapshot();Refuse([&]{(void)Lease::Acquire(factory,deps);});Require(snapshot==Snapshot());
        void*h=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL);Require(h);
        auto count=Symbol<std::uint64_t(*)(unsigned) noexcept>(h,"AEHL_TestCount");
        auto seed=Symbol<void(*)()>(h,"AEHL_TestSeed");auto drop=Symbol<void(*)() noexcept>(h,"AEHL_TestDrop");
        auto mode=Symbol<void(*)(int) noexcept>(h,"AEHL_TestMode");
        auto use=Symbol<std::uint64_t(*)(std::uintptr_t) noexcept>(h,"AEHL_TestUse");
        Symbol<void(*)(void(*)(int) noexcept) noexcept>(h,"AEHL_TestEvent")(Event);
        const std::string run=argv[16];
        if(run=="--absent") {
            const auto before=Snapshot();Refuse([&]{(void)Lease::Acquire(factory,deps);});Require(before==Snapshot()&&count(2)==0&&count(4)==0);
            Require(dlclose(h)==0);std::cout<<"DEPENDENCY_ABSENCE PASS; absent_load=0; factory_calls=0\n";return 0;
        }
        void* providers[2]{dlopen(argv[6],RTLD_NOW|RTLD_LOCAL),dlopen(argv[11],RTLD_NOW|RTLD_LOCAL)};
        Require(providers[0]&&providers[1]);
        for(unsigned i=0;i<2;++i)Symbol<void(*)(void(*)(int) noexcept) noexcept>(providers[i],"AEHL_TestDependencyEvent")(Event);
        if(run=="--bad") {
            Refuse([&]{(void)Lease::Acquire(factory,deps);});Require(count(2)==0&&count(4)==0);
            Require(dlclose(providers[1])==0&&dlclose(providers[0])==0&&dlclose(h)==0);
            std::cout<<"DEPENDENCY_BIND_REFUSAL PASS; factory_calls=0\n";return 0;
        }
        for(unsigned i=0;i<2;++i)callbacks[i]=Symbol<void(*)() noexcept>(providers[i],"AEHL_OwnedDependencyTeardown");
        Symbol<void(*)(void(*)() noexcept) noexcept>(h,"AEHL_TestDependentTeardown")(SafeTeardown);
        if(run=="--wrong-reset"||run=="--wrong-move") {
            seed();
            auto value=Lease::Acquire(factory,deps);std::set_terminate([]{std::_Exit(events.empty()?86:87);});
            std::thread invalid([&]{if(run=="--wrong-reset")value.Reset();else{auto moved=std::move(value);(void)moved;}});
            invalid.join();return 88;
        }
        Require(run=="--good"||run=="--reentrant-move");
        {auto empty=Lease::Acquire(factory,deps);Require(empty.Diagnostic().presence==factory_receiver_reference::Presence::Absent);}
        Require(count(0)==0&&count(2)==0&&count(4)==1&&events.empty());seed();
        Refuse([&]{(void)Lease::Acquire(ae256_factory_reference_identity::ReviewedProfile(),deps);});
        Refuse([&]{(void)Lease::Acquire(factory,{});});
        Refuse([&]{(void)Lease::Acquire(factory,{deps[0],deps[0]});});
        for(unsigned i=0;i<6;++i){auto bad=deps;
            if(i==0)bad[1].pin.sha256[0]^=1;
            if(i==1)bad[1].uuid[0]^=1;
            if(i==2)bad[1].spans[0].sha256[0]^=1;
            if(i==3)std::swap(bad[1].spans[0].entry.tag,bad[1].spans[1].entry.tag);
            if(i==4)bad[1].anchor="_foreign_anchor";
            if(i==5)bad[1].spans[0].entry.size+=4;
            Refuse([&]{(void)Lease::Acquire(factory,bad);});Require(count(2)==0&&count(4)==1);
        }
        bool refused=false;std::thread worker([&]{try{(void)Lease::Acquire(factory,deps);}catch(const std::exception&){refused=true;}});worker.join();Require(refused&&count(2)==0);
        mode(3);bool caught=false;try{(void)Lease::Acquire(factory,deps);}catch(const std::runtime_error&e){caught=std::string(e.what())=="owned-before-construction";}
        Require(caught&&count(4)==1&&events.empty());
        mode(1);Refuse([&]{(void)Lease::Acquire(factory,deps);});Require(count(2)==1&&count(3)==1&&count(1)==0);
        mode(0);auto first=Lease::Acquire(factory,deps);const auto slot=first.SlotAddress();auto second=Lease::Acquire(factory,deps);
        second=std::move(first);Require(second.SlotAddress()==slot&&use(slot)==73);Refuse([&]{(void)first.Diagnostic();});
        auto last=std::move(second);Require(last.SlotAddress()==slot);Refuse([&]{(void)second.Diagnostic();});
        // Only an owned provider file is replaced atomically, never mapped truncation.
        {const auto path=deps[1].pin.path;std::ifstream input(path,std::ios::binary);Bytes bytes(std::istreambuf_iterator<char>(input),{});
         std::ofstream out(path+".changed",std::ios::binary);out.write(reinterpret_cast<const char*>(bytes.data()),bytes.size());out.put('x');out.close();
         Require(std::rename(path.c_str(),(path+".backup").c_str())==0&&std::rename((path+".changed").c_str(),path.c_str())==0);
         Refuse([&]{(void)last.Diagnostic();});Require(std::remove(path.c_str())==0&&std::rename((path+".backup").c_str(),path.c_str())==0);}
        drop();Require(dlclose(providers[1])==0&&dlclose(providers[0])==0&&dlclose(h)==0);Require(!unloaded[0]&&!unloaded[1]);
        Require(last.Diagnostic().presence==factory_receiver_reference::Presence::Present&&use(slot)==73);
        const auto n=events.size();reentry_target=&last;
        if(run=="--reentrant-move") {reentry_move=true;std::set_terminate([]{std::_Exit(!unloaded[0]&&!unloaded[1]&&events.size()>=2&&events.back()==30?86:87);});}
        last.Reset();reentry_target=nullptr;
        std::cout<<"cleanup_events:";for(auto i=n;i<events.size();++i)std::cout<<' '<<events[i];std::cout<<'\n';
        Require(events.size()==n+7&&events[n]==2&&events[n+1]==30&&events[n+2]==40&&events[n+3]==1&&events[n+4]==3&&events[n+5]==41&&events[n+6]==31);
        Require(unloaded[0]&&unloaded[1]);
        std::cout<<"DEPENDENCY_LEASE PASS; actual_two_provider_callbacks_before_unload; reverse_close; stable_moves; partial_error_cleanup; Adobe_calls=0\n";
        return 0;
    } catch(const std::exception&e) {std::cerr<<"REFUSED dependency lease: "<<e.what()<<'\n';return 1;}
}
