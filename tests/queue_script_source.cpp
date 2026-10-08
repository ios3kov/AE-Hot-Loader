#include "../experiments/startup_calibration/QueueControl.hpp"
#include <iostream>
int main() {
    try {
        if (startup_queue::Quote("a\"\\b")!="\"a\\\"\\\\b\"") return 1;
        bool rejected=false;
        try {startup_queue::Quote("bad\n");} catch(const std::invalid_argument&) {rejected=true;}
        if(!rejected) return 1;
        std::cout<<startup_queue::Script("own fixture","own.match","/owned/output",4000000000ULL,7);
        return 0;
    } catch (...) {return 1;}
}
