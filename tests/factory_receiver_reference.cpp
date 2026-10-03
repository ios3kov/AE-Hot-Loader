#include "../experiments/ordinary_discovery/FactoryReceiverReference.hpp"
#include <array>
#include <atomic>
#include <cstring>
#include <iostream>
#include <memory>
#include <thread>
using namespace factory_receiver_reference;
static Bytes Tuple(std::uint64_t primary, std::uint64_t owner, std::uint64_t token) {
    Bytes b{}; const std::array<std::uint64_t,3> fields{{primary,owner,token}};
    for (std::size_t i=0;i<3;++i) for (unsigned j=0;j<8;++j) b[i*8+j]=static_cast<unsigned char>(fields[i]>>(j*8));
    return b;
}
template<class F> static void Refuse(F f) { bool failed=false;try{f();}catch(const std::exception&){failed=true;}Require(failed); }
struct Unknown { virtual ~Unknown()=default; virtual int Value() const=0; };
struct Factory:Unknown {
    int* destroyed;
    explicit Factory(int* d):destroyed(d){}
    ~Factory() override { ++*destroyed; }
    int Value() const override { return 73; }
};
struct OwnedBlock {
    // An owned layout token/prefix, NOT the standard library's control block.
    std::array<std::uint64_t,3> prefix{};
    Factory object;
    explicit OwnedBlock(int* d):object(d){}
};
int main(int argc,char**argv) {
 try {
    Require(argc==2); const std::string mode=argv[1];
    const auto layout=ReviewedAE256Layout();
    auto b=Tuple(0x1018,0x1018,0x1000);const auto d=Decode(b,layout);
    Require(d.presence==Presence::Present && d.primary==0x1018 && d.unknown_base==d.primary && d.control==0x1000);
    const auto none=Decode(Tuple(0,0,0),layout);Require(none.presence==Presence::Absent);
    for(const auto bad:{Tuple(0,0x1018,0x1000),Tuple(0x1018,0,0x1000),Tuple(0x1018,0x1018,0),
                        Tuple(0x1019,0x1019,0x1001),Tuple(0x1018,0x1050,0x1000),
                        Tuple(0x1018,0x1018,0x2000),Tuple(8,8,UINT64_MAX-7)})
        Refuse([&]{(void)Decode(bad,layout);});
    auto wrong=layout;wrong.unknown_base_adjustment=0x38;Refuse([&]{(void)Decode(b,wrong);});
    wrong=layout;wrong.object_from_control=UINT64_MAX;Refuse([&]{(void)Decode(b,wrong);});
    std::cout<<"COPIED_RECEIVER_REFERENCE PASS; diagnostic_shape_only\n";
    if(mode=="--owned") {
        int destroyed=0;
        auto block=std::make_shared<OwnedBlock>(&destroyed);std::weak_ptr<OwnedBlock> weak=block;
        Factory* object=&block->object;Unknown* unknown=object;
        const auto token=reinterpret_cast<std::uintptr_t>(block.get());
        Require(reinterpret_cast<std::uintptr_t>(object)==token+0x18 && object==unknown);
        const auto copied=Tuple(reinterpret_cast<std::uintptr_t>(object),reinterpret_cast<std::uintptr_t>(unknown),token);
        const auto actual=Decode(copied,layout);Require(actual.primary==reinterpret_cast<std::uintptr_t>(object));
        // The real guard is acquired from a typed owned weak_ptr, never from decoded integers.
        auto retained=weak.lock();Require(bool(retained));
        std::shared_ptr<Unknown> interface(retained,unknown);
        block.reset();retained.reset();Require(destroyed==0 && !weak.expired() && interface->Value()==73);
        auto moved=std::move(interface);Require(!interface && moved->Value()==73);
        moved.reset();Require(destroyed==1 && weak.expired() && !weak.lock());
        // Stale bytes still pass shape checks: decoder supplies NO lifetime attestation.
        Require(Decode(copied,layout).primary==actual.primary && destroyed==1);
        auto replacement=std::make_shared<OwnedBlock>(&destroyed);
        Require(weak.expired() && !weak.lock()); // replacement cannot resurrect the old owner
        replacement.reset();Require(destroyed==2);
        std::cout<<"OWNED_RECEIVER_LIFETIME PASS; std_cpp_owner_only; stale_shape_is_not_liveness; Adobe_calls=0\n";
    } else Require(mode=="--copied");
    return 0;
 } catch(const std::exception&) { std::cerr<<"REFUSED receiver reference\n";return 1; }
}
