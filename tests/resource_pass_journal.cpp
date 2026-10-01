// Real temporary files and child processes; synthetic host/spec/search only.
#include "../experiments/ordinary_discovery/ResourcePassJournal.hpp"
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
#include <signal.h>
#include <sys/resource.h>
#include <sys/wait.h>
using namespace resource_pass;
namespace fs = std::filesystem;
static void Check(bool value) { if (!value) throw std::runtime_error("assertion"); }
template<class F> static void Rejected(F f) { bool failed=false; try { f(); } catch (...) { failed=true; } Check(failed); }
static std::string Read(const fs::path& p) { std::ifstream f(p, std::ios::binary); return {std::istreambuf_iterator<char>(f), {}}; }
static void Write(const fs::path& p, const std::string& bytes) { std::ofstream f(p, std::ios::binary); f << bytes; Check(bool(f)); }
static void Wait(pid_t pid, int expected) { int status=0; Check(::waitpid(pid,&status,0)==pid && WIFEXITED(status) && WEXITSTATUS(status)==expected); }
static Plan TestPlan() {
    Plan p; p.run_id="resource-pass-"+std::string(32,'1'); p.source_commit=std::string(40,'2');
    p.bridge_sha256=std::string(64,'3'); p.fixture_manifest_sha256=std::string(64,'4');
    p.executable="/owned/host/After Effects"; p.root="/owned/fresh/scan-root"; p.match="AEHL.Embedded.123456789abc";
    for (const auto& key : {"AfterEffects","FILE","FLT","MEE","PLUG","PluginSupport","aelib"}) p.images[key]=std::string(64,'5');
    return p;
}
struct Model final : JournaledBackend {
    Plan p=TestPlan(); Approval a{p,true,true}; Observation base;
    fs::path dir; int creates=0, searches=0, releases=0, observations=0;
    bool search_throws=false, release_fails=false; std::uint64_t clock=1;
    std::function<void()> on_create, on_search, on_release;
    explicit Model(const fs::path& d) : JournaledBackend(d.string()), dir(d) {
        base.pid=123; base.process_start="synthetic-start"; base.executable=p.executable;
        base.version="25.6x101"; base.build=101; base.arch="arm64"; base.bridge_sha256=p.bridge_sha256;
        base.images=p.images;
        base.runtime_images={{p.executable,0x1000,0},
            {"/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks/PLUG.dylib",0x2000,16}};
        base.main_thread=true; base.unsaved=true; base.dirty=false;
        base.rendering=false; base.revision=1; base.registry={"ADBE.A","ADBE.B"};
    }
    std::uint64_t now_ms() override { return clock++; }
    Observation observe() override { ++observations; auto o=base; if (searches) o.registry.push_back(p.match); return o; }
    void verify_fixture(const Plan& q) override { Check(q.root==p.root); } // no fixture/AE proof
    Spec create_spec(const std::string& root) override { Check(root==p.root); ++creates; if (on_create) on_create(); return {this}; }
    std::string spec_path(Spec s) override { Check(s.value==this); return p.root; }
    SearchResult search_one_root(Spec s, std::uint64_t) override {
        Check(s.value==this); ++searches; if (on_search) on_search();
        if (search_throws) throw std::runtime_error("synthetic search error");
        return {0,0,false};
    }
    bool release_spec(Spec s) noexcept override { if (s.value!=this) return false; ++releases; if (on_release) on_release(); return !release_fails; }
    Result run() { return RunJournaled(p,a,*this); }
};
int main(int argc, char** argv) {
    if (argc!=2) return 2;
    const fs::path root(argv[1]);
    int count=0;
    auto test = [&](const std::string& name, const std::function<void(const fs::path&)>& body) {
        const auto d=root/name; Check(fs::create_directory(d)); Check(::chmod(d.c_str(),0700)==0);
        body(d); ++count; std::cout << "PASS " << name << std::endl;
    };
    try {
        test("complete-journal-before-returned-pass", [](const fs::path& d) {
            Model b(d); Check(b.run().status=="PASS" && b.searches==1 && b.releases==1);
            std::set<std::string> names;
            for (const auto& f:fs::directory_iterator(d)) {
                names.insert(f.path().filename()); struct stat st{}; Check(::lstat(f.path().c_str(),&st)==0);
                Check(S_ISREG(st.st_mode) && (st.st_mode&0777)==0600 && st.st_nlink==1);
                const auto bytes=Read(f.path()); Check(bytes.rfind("AEHL-RESOURCE-JOURNAL-1\n",0)==0);
                Check(bytes.size()>17 && bytes.substr(bytes.size()-17)=="\nEND-AEHL-RECORD\n");
            }
            Check(names==std::set<std::string>{"claim.txt","before.txt","call-started.txt","native.txt","after.txt","result.txt"});
            Check(Read(d/"claim.txt").find(b.p.root)!=std::string::npos);
            Check(Read(d/"native.txt").find("scope=21:resource-registration\n")!=std::string::npos);
            Check(Read(d/"native.txt").find("code=1:0\n")!=std::string::npos);
            Check(Read(d/"result.txt").find("search_observed=1:1\n")!=std::string::npos);
            Check(Read(d/"result.txt").find("status=4:PASS\n")!=std::string::npos);
        });
        test("new-backend-cannot-replay-completed-run", [](const fs::path& d) {
            { Model a(d); Check(a.run().status=="PASS"); }
            const auto original=Read(d/"result.txt"); Model b(d);
            Check(b.run().status=="BLOCKED" && b.creates==0 && b.searches==0);
            Check(Read(d/"result.txt")==original);
        });
        test("same-backend-cannot-replay", [](const fs::path& d) {
            Model b(d); Check(b.run().status=="PASS"); Check(b.run().status=="BLOCKED" && b.searches==1);
        });
        test("partial-claim-is-never-overwritten", [](const fs::path& d) {
            Write(d/"claim.txt","partial"); Model b(d); Check(b.run().status=="BLOCKED" && b.creates==0);
            Check(Read(d/"claim.txt")=="partial");
        });
        test("orphan-marker-blocks-replay", [](const fs::path& d) {
            Write(d/"call-started.txt","unknown"); Model b(d); Check(b.run().status=="BLOCKED" && b.searches==0);
        });
        test("foreign-directory-entry-is-preserved", [](const fs::path& d) {
            Write(d/"keep.txt","keep"); Model b(d); Check(b.run().status=="BLOCKED" && Read(d/"keep.txt")=="keep");
        });
        test("symlink-claim-cannot-touch-target", [](const fs::path& d) {
            const auto target=d.parent_path()/"external-target"; Write(target,"keep"); fs::create_symlink(target,d/"claim.txt");
            Model b(d); Check(b.run().status=="BLOCKED" && Read(target)=="keep" && fs::is_symlink(d/"claim.txt"));
        });
        test("fifo-claim-cannot-block-reader", [](const fs::path& d) {
            Check(::mkfifo((d/"claim.txt").c_str(),0600)==0); Model b(d); Check(b.run().status=="BLOCKED");
        });
        test("hardlinked-claim-is-preserved", [](const fs::path& d) {
            const auto target=d.parent_path()/"hardlink-target"; Write(target,"keep"); fs::create_hard_link(target,d/"claim.txt");
            Model b(d); Check(b.run().status=="BLOCKED" && Read(target)=="keep");
        });
        test("nonprivate-directory-rejected", [](const fs::path& d) {
            Check(::chmod(d.c_str(),0755)==0); Rejected([&]{ Model b(d); }); Check(fs::is_empty(d));
        });
        test("symlink-directory-rejected", [](const fs::path& d) {
            const auto alias=d.parent_path()/"directory-alias"; fs::create_directory_symlink(d,alias);
            Rejected([&]{ Model b(alias); }); Check(fs::is_empty(d));
        });
        test("symlink-parent-rejected", [](const fs::path& d) {
            const auto nested=d/"nested"; fs::create_directory(nested); ::chmod(nested.c_str(),0700);
            const auto alias=d.parent_path()/"parent-alias"; fs::create_directory_symlink(d,alias);
            Rejected([&]{ Model b(alias/"nested"); }); Check(fs::is_empty(nested));
        });
        test("directory-replacement-stops-before-search", [](const fs::path& d) {
            Model b(d); b.on_create=[&]{fs::rename(d,d.string()+"-old");fs::create_directory(d);::chmod(d.c_str(),0700);};
            Check(b.run().status=="FAIL" && b.searches==0 && b.releases==1 && fs::is_empty(d));
        });
        test("claim-tampering-stops-before-search", [](const fs::path& d) {
            Model b(d); b.on_create=[&]{Write(d/"claim.txt","changed");};
            Check(b.run().status=="FAIL" && b.searches==0 && b.releases==1);
        });
        test("claim-removal-stops-before-search", [](const fs::path& d) {
            Model b(d); b.on_create=[&]{fs::remove(d/"claim.txt");}; Check(b.run().status=="FAIL" && b.searches==0);
        });
        test("record-inode-replacement-stops-search", [](const fs::path& d) {
            Model b(d); b.on_create=[&]{ const auto bytes=Read(d/"claim.txt"); fs::rename(d/"claim.txt",d.parent_path()/"old-claim"); Write(d/"claim.txt",bytes); ::chmod((d/"claim.txt").c_str(),0600); };
            Check(b.run().status=="FAIL" && b.searches==0);
        });
        test("record-hardlink-added-stops-search", [](const fs::path& d) {
            Model b(d); b.on_create=[&]{fs::create_hard_link(d/"claim.txt",d.parent_path()/"new-link");}; Check(b.run().status=="FAIL" && b.searches==0);
        });
        test("permission-change-stops-search", [](const fs::path& d) {
            Model b(d); b.on_create=[&]{::chmod((d/"claim.txt").c_str(),0644);}; Check(b.run().status=="FAIL" && b.searches==0);
        });
        test("search-exception-keeps-fail-evidence", [](const fs::path& d) {
            Model b(d); b.search_throws=true; Check(b.run().status=="FAIL" && b.searches==1 && b.releases==1);
            Check(fs::exists(d/"after.txt") && Read(d/"result.txt").find("status=4:FAIL\n")!=std::string::npos);
            Model retry(d); Check(retry.run().status=="BLOCKED" && retry.searches==0);
        });
        test("cleanup-failure-cannot-pass", [](const fs::path& d) {
            Model b(d); b.release_fails=true; Check(b.run().status=="FAIL" && b.releases==1);
            Check(Read(d/"result.txt").find("cleanup_ok=1:0\n")!=std::string::npos);
        });
        test("final-evidence-failure-revokes-pass", [](const fs::path& d) {
            Model b(d); b.on_search=[&]{Write(d/"result.txt","foreign");}; auto r=b.run();
            Check(r.status=="FAIL" && r.stage=="evidence" && b.searches==1 && Read(d/"result.txt")=="foreign");
        });
        test("new-authorization-still-required", [](const fs::path& d) {
            Model b(d); b.a.new_private_call_authorized=false; Check(b.run().status=="BLOCKED" && b.creates==0 && fs::is_empty(d));
        });
        test("changed-plan-cannot-write-call-marker", [](const fs::path& d) {
            Model b(d); b.claim(b.p,b.base); b.save_observation("before",b.base); auto other=b.p; other.root="/other/scan-root";
            Rejected([&]{b.mark_call_started(other,b.base);}); Check(!fs::exists(d/"call-started.txt"));
        });
        test("unknown-observation-name-rejected", [](const fs::path& d) {
            Model b(d); b.claim(b.p,b.base); Rejected([&]{b.save_observation("../escape",b.base);}); Check(!fs::exists(d.parent_path()/"escape"));
        });
        test("duplicate-before-record-rejected", [](const fs::path& d) {
            Model b(d); b.claim(b.p,b.base); b.save_observation("before",b.base); const auto bytes=Read(d/"before.txt");
            Rejected([&]{b.save_observation("before",b.base);}); Check(Read(d/"before.txt")==bytes);
        });
        test("incomplete-pass-record-rejected", [](const fs::path& d) {
            Model b(d); b.claim(b.p,b.base); Result r; r.claimed=true; r.status="PASS";
            Rejected([&]{b.finish(r);}); Check(!fs::exists(d/"result.txt"));
        });
        test("unicode-directory-and-root", [](const fs::path& d) {
            const auto nested=d/"проверка с пробелами"; fs::create_directory(nested); ::chmod(nested.c_str(),0700);
            Model b(nested); b.p.root="/owned/тест с пробелами/scan-root"; b.a.scope=b.p;
            Check(b.run().status=="PASS" && Read(nested/"claim.txt").find(b.p.root)!=std::string::npos);
        });
        test("process-exit-after-claim-prevents-replay", [](const fs::path& d) {
            const auto pid=::fork(); Check(pid>=0); if (!pid) { try {Model b(d);b.claim(b.p,b.base);::_exit(0);}catch(...){::_exit(1);} }
            Wait(pid,0); Model b(d); Check(b.run().status=="BLOCKED" && b.creates==0 && !fs::exists(d/"call-started.txt"));
        });
        test("process-exit-after-marker-prevents-replay", [](const fs::path& d) {
            const auto pid=::fork(); Check(pid>=0); if (!pid) { try {Model b(d);b.claim(b.p,b.base);b.save_observation("before",b.base);b.mark_call_started(b.p,b.base);::_exit(0);}catch(...){::_exit(1);} }
            Wait(pid,0); Model b(d); Check(b.run().status=="BLOCKED" && b.searches==0 && fs::exists(d/"call-started.txt"));
        });
        test("inherited-journal-object-rejected", [](const fs::path& d) {
            Model b(d); b.claim(b.p,b.base); const auto pid=::fork(); Check(pid>=0);
            if (!pid) { try {b.save_observation("before",b.base);::_exit(1);}catch(...){::_exit(0);} }
            Wait(pid,0); Check(!fs::exists(d/"before.txt"));
        });
        test("real-partial-write-error-prevents-replay", [](const fs::path& d) {
            const auto pid=::fork(); Check(pid>=0);
            if (!pid) { ::signal(SIGXFSZ,SIG_IGN); struct rlimit limit{};
                if (::getrlimit(RLIMIT_FSIZE,&limit)) ::_exit(2);
                limit.rlim_cur=64;
                if (::setrlimit(RLIMIT_FSIZE,&limit)) ::_exit(3);
                try {Model b(d);auto r=b.run();::_exit(r.status=="BLOCKED" && b.creates==0 ? 0 : 1);}catch(...){::_exit(4);} }
            Wait(pid,0); Check(fs::file_size(d/"claim.txt")>0 && fs::file_size(d/"claim.txt")<=64);
            Model b(d); Check(b.run().status=="BLOCKED" && b.searches==0);
        });
        test("eight-process-race-has-one-winner", [](const fs::path& d) {
            int barrier[2]; Check(::pipe(barrier)==0); std::vector<pid_t> pids;
            for (int i=0;i<8;++i) {
                const auto pid=::fork(); Check(pid>=0);
                if (!pid) { ::close(barrier[1]); char c; if (::read(barrier[0],&c,1)!=1) ::_exit(3); ::close(barrier[0]);
                    try {Model b(d);const auto r=b.run();::_exit(r.status=="PASS" ? 0 : r.status=="BLOCKED" ? 10 : 2);}catch(...){::_exit(4);} }
                pids.push_back(pid);
            }
            ::close(barrier[0]); Check(::write(barrier[1],"12345678",8)==8); ::close(barrier[1]); int winners=0;
            for (const auto pid:pids) {int status=0;Check(::waitpid(pid,&status,0)==pid && WIFEXITED(status));const int code=WEXITSTATUS(status);Check(code==0 || code==10);if (!code) ++winners;}
            Check(winners==1 && Read(d/"result.txt").find("status=4:PASS\n")!=std::string::npos);
        });
        std::cout << "RESOURCE_JOURNAL_TESTS=" << count << " PASS; scope=real-files-processes-synthetic-host\n";
        return 0;
    } catch (const std::exception& e) { std::cerr << "FAIL after " << count << ": " << e.what() << '\n'; return 1; }
}
