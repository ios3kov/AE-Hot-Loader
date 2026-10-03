#include "../experiments/ordinary_discovery/NativeClassRefCallLease.hpp"
#include "../experiments/ordinary_discovery/AE256FactoryReferenceIdentityProfile.hpp"
#include <fstream>
#include <iterator>
#include <iostream>
#include <thread>
#include <vector>
using namespace classref_call_lease;
static std::vector<int> events;
static void Event(int n) noexcept { events.push_back(n); }
template<class F> static void Refuse(F f) {
    bool refused=false; try { f(); } catch(const std::exception&) { refused=true; } Require(refused);
}
template<class T> static T Symbol(void* h,const char* n) {
    auto p=dlsym(h,n); Require(p); return reinterpret_cast<T>(p);
}
int main(int argc,char** argv) {
    try {
        Require(argc==7); events.reserve(32);
        std::ifstream f(argv[1],std::ios::binary); Require(bool(f));
        const Bytes bytes(std::istreambuf_iterator<char>(f),{});
        std::vector<Entry> entries{{"acquire",std::stoull(argv[2],nullptr,0),std::stoull(argv[3],nullptr,0)},
                                   {"destroy",std::stoull(argv[4],nullptr,0),std::stoull(argv[5],nullptr,0)}};
        std::sort(entries.begin(),entries.end(),[](const Entry& a,const Entry& b){return a.vm<b.vm;});
        const auto layout=Describe(bytes,Anchor,entries);
        Profile p{{argv[1],Hash(bytes)},Anchor,layout.image.uuid,{}};
        for(const auto& e:entries) p.spans.push_back({e,Hash(SpanBytes(bytes,layout,e.tag))});
        const auto before=Snapshot(); Refuse([&]{(void)Lease::Acquire(p);}); Require(before==Snapshot());
        const auto ae=ae256_factory_reference_identity::ReviewedProfile();
        Require(ae.spans.size()==2 && ae.spans[0].entry.vm==0x3e9c && ae.spans[0].entry.size==96);
        Refuse([&]{(void)Lease::Acquire(ae);}); Require(before==Snapshot()); // no Adobe file/runtime access
        void* handle=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL); Require(handle);
        auto count=Symbol<std::uint64_t(*)(unsigned) noexcept>(handle,"AEHL_TestCount");
        auto seed=Symbol<void(*)()>(handle,"AEHL_TestSeed");
        auto drop=Symbol<void(*)() noexcept>(handle,"AEHL_TestDrop");
        auto mode=Symbol<void(*)(int) noexcept>(handle,"AEHL_TestMode");
        auto use=Symbol<std::uint64_t(*)(std::uintptr_t) noexcept>(handle,"AEHL_TestUse");
        Symbol<void(*)(void(*)(int) noexcept) noexcept>(handle,"AEHL_TestEvent")(Event);
        const std::string runmode=argv[6];
        if(runmode=="--wrong-reset" || runmode=="--wrong-move") {
            seed(); auto owned=Lease::Acquire(p);
            std::set_terminate([]{std::_Exit(events.empty()?86:87);});
            std::thread invalid([&]{
                if(runmode=="--wrong-reset") owned.Reset();
                else {auto moved=std::move(owned);(void)moved;}
            });
            invalid.join();return 88;
        }
        if(runmode=="--bad") {
            seed(); Refuse([&]{(void)Lease::Acquire(p);}); Require(count(2)==0 && count(4)==0 && count(5)==0);
            drop(); Require(dlclose(handle)==0); std::cout<<"CLASSREF_BIND_REFUSAL PASS; target_calls=0\n"; return 0;
        }
        Require(runmode=="--good");
        { auto empty=Lease::Acquire(p); Require(empty.Diagnostic().presence==factory_receiver_reference::Presence::Absent); }
        Require(count(0)==0 && count(2)==0 && count(4)==1 && count(5)==0);
        seed();
        for(unsigned i=0;i<7;++i) {
            auto bad=p;
            if(i==0) bad.pin.sha256[0]^=1;
            if(i==1) bad.uuid[0]^=1;
            if(i==2) bad.spans[0].sha256[0]^=1;
            if(i==3) std::swap(bad.spans[0].entry.tag,bad.spans[1].entry.tag);
            if(i==4) bad.anchor=ae.anchor;
            if(i==5) bad.spans[0].entry.size+=4;
            if(i==6) bad.spans[0].sha256.fill(0);
            Refuse([&]{(void)Lease::Acquire(bad);}); Require(count(2)==0 && count(4)==1 && count(5)==0);
        }
        bool refused=false;
        std::thread worker([&]{try{(void)Lease::Acquire(p);}catch(const std::exception&){refused=true;}});
        worker.join(); Require(refused && count(2)==0);
        mode(3); bool caught=false;
        try { (void)Lease::Acquire(p); } catch(const std::runtime_error& e) { caught=std::string(e.what())=="owned-before-construction"; }
        Require(caught && count(2)==0 && count(4)==1 && count(6)==0); // real unwind through assembly CFI
        for(int m:{1,2}) {
            mode(m); Refuse([&]{(void)Lease::Acquire(p);}); Require(count(2)==std::uint64_t(m) && count(3)==std::uint64_t(m));
        }
        mode(0);
        auto first=Lease::Acquire(p); const auto slot=first.SlotAddress(); const auto original=first.Diagnostic();
        Require(original.presence==factory_receiver_reference::Presence::Present && use(slot)==73);
        auto second=Lease::Acquire(p); drop(); Require(count(1)==0);
        second=std::move(first); Require(second.SlotAddress()==slot && use(slot)==73); Refuse([&]{(void)first.Diagnostic();});
        auto final=std::move(second); Require(final.SlotAddress()==slot && use(slot)==73);
        // Replace only this owned file atomically; mapped original is unchanged.
        {
            const std::string changed=std::string(argv[1])+".changed",backup=std::string(argv[1])+".backup";
            std::ofstream replacement(changed,std::ios::binary);
            replacement.write(reinterpret_cast<const char*>(bytes.data()),bytes.size());replacement.put('x');replacement.close();
            Require(std::rename(argv[1],backup.c_str())==0 && std::rename(changed.c_str(),argv[1])==0);
            Refuse([&]{(void)final.Diagnostic();});
            Require(std::remove(argv[1])==0 && std::rename(backup.c_str(),argv[1])==0);
        }
        final.Reset(); Require(count(1)==1 && count(3)==4 && count(6)==0);
        { auto expired=Lease::Acquire(p); Require(expired.Diagnostic().presence==factory_receiver_reference::Presence::Absent); }
        Require(count(0)==1 && count(5)==0);
        seed(); auto last=Lease::Acquire(p); const auto lastslot=last.SlotAddress(); drop();
        Require(dlclose(handle)==0); handle=nullptr; Require(use(lastslot)==73 && last.Diagnostic().presence==factory_receiver_reference::Presence::Present);
        const auto n=events.size(); last.Reset(); Require(events.size()>=n+2 && events[n]==2 && events[n+1]==1);
        const bool unload=events.size()>n+2 && events[n+2]==3;
        std::cout<<"CLASSREF_CALL_LEASE PASS; real_nontrivial_result; false_flag; x8_result; whole_base_destroy; "
                    "stable_slot_moves; unwind_no_unconstructed_destroy; release_before_image_close; Adobe_calls=0; unload_observed="<<unload<<'\n';
        return 0;
    } catch(const std::exception& e) { std::cerr<<"REFUSED classref call: "<<e.what()<<'\n'; return 1; }
}
