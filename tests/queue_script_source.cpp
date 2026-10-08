#include "../experiments/startup_calibration/QueueControl.hpp"
#include <iostream>
int main(int argc, char** argv) {
    try {
        if(argc==2 && std::string(argv[1])=="--revision") {
            char input[4096]{};
            std::cin.read(input,sizeof(input));
            if(std::cin.gcount()>4095) return 1;
            std::cout<<startup_queue::RevisionLine(std::string(input,static_cast<std::size_t>(std::cin.gcount())));
            return 0;
        }
        if(argc!=1) return 1;
        if(startup_queue::RevisionLine("queue\nrevision=34\ninventory_complete=YES\ntemplates=png:PNG%20Sequence:RGB;\n")!="34\n") return 1;
        if(startup_queue::RevisionLine("queue\nrevision=7\n")!="7\n") return 1;
        for(const auto* bad : {"queue\n", "queue\nrevision=0\n", "queue\nrevision=07\n",
             "queue\nrevision=7", "queue\nrevision=-7\n", "queue\nrevision=7x\n",
             "queue\nrevision=7\nrevision=8\n", "queue\nrevision=9007199254740992\n"}) {
            bool refused=false;
            try {startup_queue::RevisionLine(bad);} catch(const std::invalid_argument&) {refused=true;}
            if(!refused) return 1;
        }
        if (startup_queue::Quote("a\"\\b")!="\"a\\\"\\\\b\"") return 1;
        bool rejected=false;
        try {startup_queue::Quote("bad\n");} catch(const std::invalid_argument&) {rejected=true;}
        if(!rejected) return 1;
        std::cout<<startup_queue::Script("own fixture","own.match","/owned/output",4000000000ULL,7);
        return 0;
    } catch (...) {return 1;}
}
