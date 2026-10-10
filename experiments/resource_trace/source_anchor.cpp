// Owned, cooperative child only. Kernel file metadata; no debugger or target memory.
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/proc_info.h>
#include <sys/wait.h>
#include <libproc.h>
#include <unistd.h>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <array>
#include <cerrno>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {
void require(bool ok, const char* reason) { if (!ok) throw std::runtime_error(reason); }
struct Fd {
    int value;
    explicit Fd(int x=-1): value(x) {}
    ~Fd() { if (value>=0) close(value); }
    Fd(const Fd&)=delete; Fd& operator=(const Fd&)=delete;
    void reset() { if(value>=0) close(value); value=-1; }
};
struct Message { int phase=0, fd=-1, count=0; std::array<char,64> bytes{}; };
void send(int fd, const Message& m) {
    ssize_t n;
    do { n=write(fd, &m, sizeof(m)); } while(n<0 && errno==EINTR);
    require(n==sizeof(m), "PIPE_WRITE_FAILED");
}
Message receive(int fd) {
    Message m; size_t offset=0;
    while(offset<sizeof(m)) {
        pollfd p{fd,POLLIN,0}; int ready;
        do { ready=poll(&p,1,5000); } while(ready<0 && errno==EINTR);
        require(ready==1 && (p.revents&(POLLIN|POLLHUP)), "PIPE_WAIT_FAILED");
        ssize_t n=read(fd,reinterpret_cast<char*>(&m)+offset,sizeof(m)-offset);
        if(n<0 && errno==EINTR) continue;
        require(n>0, "PIPE_READ_FAILED"); offset+=static_cast<size_t>(n);
    }
    return m;
}
proc_bsdinfo identity(pid_t pid) {
    proc_bsdinfo info{};
    require(proc_pidinfo(pid,PROC_PIDTBSDINFO,0,&info,sizeof(info))==sizeof(info), "PROCESS_QUERY_FAILED");
    require(info.pbi_pid==static_cast<uint32_t>(pid) && info.pbi_ppid==static_cast<uint32_t>(getpid()) &&
            info.pbi_uid==getuid(), "NOT_OWNED_CHILD");
    return info;
}
bool same_process(const proc_bsdinfo& a,const proc_bsdinfo& b) {
    return a.pbi_pid==b.pbi_pid && a.pbi_start_tvsec==b.pbi_start_tvsec &&
           a.pbi_start_tvusec==b.pbi_start_tvusec;
}
vnode_fdinfo inspect(pid_t pid,int fd,const proc_bsdinfo& born) {
    require(fd>=0 && same_process(born,identity(pid)), "PROCESS_GENERATION_CHANGED");
    vnode_fdinfo info{};
    require(proc_pidfdinfo(pid,fd,PROC_PIDFDVNODEINFO,&info,sizeof(info))==sizeof(info), "FD_QUERY_FAILED");
    require(same_process(born,identity(pid)), "PROCESS_GENERATION_CHANGED");
    return info;
}
// Child reports naturally executed operations, then waits. Instrumented fixture
// events are not a passive observation of arbitrary Adobe fd lifecycle.
void child(int events,int commands,int inherited,const char* a,const char* b,const std::string& mode) {
    close(inherited);
    Fd target(open(a,O_RDWR|O_NOFOLLOW)); require(target.value>=0,"CHILD_OPEN_FAILED");
    send(events,Message{1,target.value,0,{}});
    require(receive(commands).phase==1,"FIRST_ADMISSION_DENIED");
    if(mode=="replace-fd") {
        Fd other(open(b,O_RDONLY|O_NOFOLLOW)); require(other.value>=0,"TWIN_OPEN_FAILED");
        require(dup2(other.value,target.value)==target.value,"DUP2_FAILED");
    } else if(mode=="mutate-file") {
        const char byte='X'; require(pwrite(target.value,&byte,1,0)==1,"OWNED_MUTATION_FAILED");
    }
    send(events,Message{2,target.value,0,{}});
    Message admission=receive(commands);
    if(admission.phase!=1) { send(events,Message{4,target.value,0,{}}); return; }
    Message output{3,target.value,0,{}};
    ssize_t n=read(target.value,output.bytes.data(),output.bytes.size());
    require(n>0 && n<=64,"PAYLOAD_READ_FAILED"); output.count=static_cast<int>(n);
    send(events,output);
}
bool retire(pid_t pid,int& status) {
    for(int i=0;i<600;++i) {
        pid_t result=waitpid(pid,&status,WNOHANG);
        if(result==pid) return true;
        if(result<0 && errno!=EINTR) return false;
        usleep(10000);
    }
    return false; // Preserve unexpected live child; no kill.
}
}
int main(int argc,char** argv) {
    pid_t pid=-1; int events[2]{-1,-1},commands[2]{-1,-1};
    try {
        require(argc==4,"ARGUMENTS"); const std::string mode=argv[3];
        require(mode=="none" || mode=="replace-fd" || mode=="mutate-file","VARIANT");
        signal(SIGPIPE,SIG_IGN); // Only this disposable process; no external signal.
        Fd anchor(open(argv[1],O_RDONLY|O_NOFOLLOW)); require(anchor.value>=0,"ANCHOR_OPEN_FAILED");
        struct stat initial{}; require(fstat(anchor.value,&initial)==0 && S_ISREG(initial.st_mode) &&
            initial.st_uid==getuid() && initial.st_nlink==1 && initial.st_size>0 && initial.st_size<=64,"ANCHOR_SCOPE");
        std::array<char,64> expected{};
        require(pread(anchor.value,expected.data(),expected.size(),0)==initial.st_size,"ANCHOR_BYTES");
        require(pipe(events)==0 && pipe(commands)==0,"PIPE_CREATE_FAILED");
        pid=fork(); require(pid>=0,"FORK_FAILED");
        if(pid==0) {
            close(events[0]); close(commands[1]);
            try { child(events[1],commands[0],anchor.value,argv[1],argv[2],mode); }
            catch(...) { _exit(2); }
            _exit(0);
        }
        close(events[1]); events[1]=-1; close(commands[0]); commands[0]=-1;
        const auto born=identity(pid); Message first=receive(events[0]); require(first.phase==1,"FIRST_PHASE");
        const auto first_info=inspect(pid,first.fd,born);
        require(first_info.pvi.vi_stat.vst_dev==static_cast<uint32_t>(initial.st_dev) &&
                first_info.pvi.vi_stat.vst_ino==initial.st_ino,"FIRST_SOURCE_DIFFERS");
        send(commands[1],Message{1,-1,0,{}});
        Message next=receive(events[0]); require(next.phase==2 && next.fd==first.fd,"READ_PHASE");
        const auto current=inspect(pid,next.fd,born); std::string reason="NONE";
        if(current.pvi.vi_stat.vst_dev!=first_info.pvi.vi_stat.vst_dev ||
           current.pvi.vi_stat.vst_ino!=first_info.pvi.vi_stat.vst_ino) reason="SOURCE_FILE_CHANGED";
        std::array<char,64> fresh{};
        // Holding an fd does not freeze bytes. Recheck our own source separately.
        if(reason=="NONE" && (pread(anchor.value,fresh.data(),fresh.size(),0)!=initial.st_size ||
           std::memcmp(fresh.data(),expected.data(),static_cast<size_t>(initial.st_size)))) reason="SOURCE_CONTENT_CHANGED";
        send(commands[1],Message{reason=="NONE"?1:0,-1,0,{}});
        Message result=receive(events[0]);
        const bool payload=reason=="NONE";
        require(result.phase==(payload?3:4) && result.count==(payload?initial.st_size:0),"RESULT_PHASE");
        if(payload) require(!std::memcmp(result.bytes.data(),expected.data(),static_cast<size_t>(result.count)),"READ_BYTES_DIFFER");
        close(commands[1]); commands[1]=-1; close(events[0]); events[0]=-1;
        const pid_t observed_pid=pid;
        int status=0; require(retire(pid,status),"CHILD_RETAINED_ATTENTION"); pid=-1;
        require(WIFEXITED(status) && WEXITSTATUS(status)==0,"CHILD_EXIT_FAILED");
        std::cout << "{\"status\":\"" << (payload?"OWNED_SOURCE_OBSERVED":"REFUSED")
          << "\",\"reason\":\"" << reason << "\",\"payload_reads\":" << (payload?1:0)
          << ",\"same_fd_number\":true,\"initial_device\":" << first_info.pvi.vi_stat.vst_dev
          << ",\"initial_inode\":" << first_info.pvi.vi_stat.vst_ino
          << ",\"current_device\":" << current.pvi.vi_stat.vst_dev
          << ",\"current_inode\":" << current.pvi.vi_stat.vst_ino
          << ",\"child_pid\":" << observed_pid << ",\"birth_sec\":" << born.pbi_start_tvsec
          << ",\"birth_usec\":" << born.pbi_start_tvusec
          << ",\"child_reaped\":true,\"kernel_queries\":2,\"AE_admission\":\"BLOCKED\"}\n";
        return 0;
    } catch(const std::exception& e) {
        for(int fd: events) if(fd>=0) close(fd);
        for(int fd: commands) if(fd>=0) close(fd);
        int status=0; bool reaped=pid<0 || retire(pid,status);
        std::cerr << e.what() << "; child_reaped=" << reaped << '\n'; return 2;
    }
}
