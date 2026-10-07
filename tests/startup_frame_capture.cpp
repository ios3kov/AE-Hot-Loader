// Actual SDK adapter; only our fake host callbacks run in this executable.
#include "../experiments/startup_calibration/AsyncFrameCapture.hpp"
#include "../experiments/startup_calibration/MarkerCore.hpp"
#include <iostream>
#include <thread>
#include <vector>
namespace {
int mode=0,checkins=0,disposals=0,cancels=0,region_calls=0;
std::vector<unsigned> trace_events;
std::thread::id caller_thread;
bool trace_wrong_thread=false;
std::atomic<bool> worker_release{false};
std::thread deferred_worker;
startup_frame::Capture* active_capture=nullptr;
void Trace(unsigned stage) noexcept {
    if (std::this_thread::get_id()!=caller_thread) trace_wrong_thread=true;
    // Capacity reserved before any callback/test, avoiding throwing allocation.
    if (trace_events.size()<trace_events.capacity()) trace_events.push_back(stage);
}
AEGP_AsyncFrameReadyCallback callback=nullptr;
AEGP_AsyncFrameRequestRefcon context=nullptr;
std::vector<unsigned char> pixels(288*48,0xA5);
const auto option=reinterpret_cast<AEGP_LayerRenderOptionsH>(0x1000);
const auto receipt=reinterpret_cast<AEGP_FrameReceiptH>(0x2000);
void Check(bool value) { if (!value) throw std::runtime_error("frame adapter assertion"); }
template<class R,class... Args> R Stub(Args...) { return R{}; }
void Deliver() { Check(callback(mode==10?6:5,mode==9?TRUE:FALSE,mode==8?1:0,
    mode==8?nullptr:receipt,context)==0); }
}
int main() {
    try {
        AEGP_LayerRenderOptionsSuite2 options{}; AEGP_RenderSuite5 renders{}; AEGP_WorldSuite3 worlds{};
        options.AEGP_NewFromLayer=[](AEGP_PluginID,AEGP_LayerH,AEGP_LayerRenderOptionsH* out)->A_Err {
            *out=mode==15?nullptr:option; return (mode==14||mode==15)?1:0; };
        options.AEGP_Dispose=[](AEGP_LayerRenderOptionsH h)->A_Err { Check(h==option && trace_events.back()==16);++disposals;return mode==12?1:0; };
        options.AEGP_SetTime=[](AEGP_LayerRenderOptionsH,A_Time t)->A_Err { Check(t.value==1&&t.scale==24);return 0; };
        options.AEGP_SetTimeStep=options.AEGP_SetTime; options.AEGP_SetWorldType=Stub;
        options.AEGP_SetDownsampleFactor=Stub; options.AEGP_SetMatteMode=Stub;
        options.AEGP_GetTime=[](AEGP_LayerRenderOptionsH,A_Time* out)->A_Err { *out={1,24};return mode==17?1:0; };
        options.AEGP_GetTimeStep=options.AEGP_GetTime;
        options.AEGP_GetWorldType=[](AEGP_LayerRenderOptionsH,AEGP_WorldType* out)->A_Err { *out=AEGP_WorldType_8;return 0; };
        options.AEGP_GetDownsampleFactor=[](AEGP_LayerRenderOptionsH,A_short* x,A_short* y)->A_Err { *x=1;*y=1;return 0; };
        options.AEGP_GetMatteMode=[](AEGP_LayerRenderOptionsH,AEGP_MatteMode* out)->A_Err { *out=AEGP_MatteMode_STRAIGHT;return 0; };
        const auto forbidden_region=[](AEGP_FrameReceiptH,A_LRect*)->A_Err {
            ++region_calls; return 1;
        };
        renders.AEGP_RenderAndCheckoutLayerFrame_Async=[](AEGP_LayerRenderOptionsH,
            AEGP_AsyncFrameReadyCallback fn,AEGP_AsyncFrameRequestRefcon arg,AEGP_AsyncRequestId* out)->A_Err {
            callback=fn;context=arg;*out=5;
            if(mode==1) { std::thread worker(Deliver);worker.join(); }
            else if(mode==19) deferred_worker=std::thread([] {
                while(!worker_release.load(std::memory_order_acquire)) std::this_thread::yield();
                Deliver();
            });
            else if(mode!=2 && mode!=13 && mode!=18) Deliver();
            if(mode==20) {
                // Same-thread callback has completed while Start is still on
                // stack. Reentrant consumption must stay refused before SDK.
                Check(active_capture && !active_capture->Done() && active_capture->Pending());
                Check(active_capture->Diagnostic().find("callback=PENDING\n")!=std::string::npos);
                bool refused=false;try { active_capture->Copy(); } catch(...) { refused=true; }
                Check(refused && trace_events.empty());
            }
            return mode==13?1:0; };
        renders.AEGP_CancelAsyncRequest=[](AEGP_AsyncRequestId id)->A_Err { Check(id==5);++cancels;return 0; };
        renders.AEGP_CheckinFrame=[](AEGP_FrameReceiptH h)->A_Err { Check(h==receipt && trace_events.back()==14);++checkins;return mode==11?1:0; };
        renders.AEGP_GetReceiptWorld=[](AEGP_FrameReceiptH,AEGP_WorldH* out)->A_Err {
            Check(trace_events.back()==2);*out=mode==16?nullptr:reinterpret_cast<AEGP_WorldH>(0x3000);return mode==7?1:0; };
        worlds.AEGP_GetType=[](AEGP_WorldH,AEGP_WorldType* out)->A_Err { *out=mode==3?AEGP_WorldType_16:AEGP_WorldType_8;return 0; };
        worlds.AEGP_GetSize=[](AEGP_WorldH,A_long* w,A_long* h)->A_Err { *w=mode==4?65:64;*h=48;return 0; };
        worlds.AEGP_GetRowBytes=[](AEGP_WorldH,A_u_long* out)->A_Err { *out=mode==5?255:288;return 0; };
        worlds.AEGP_GetBaseAddr8=[](AEGP_WorldH,PF_Pixel8** out)->A_Err { *out=mode==6?nullptr:reinterpret_cast<PF_Pixel8*>(pixels.data());return 0; };
        Check(startup_marker::Render(pixels.data(),64,48,288,123));
        for (mode=0;mode<21;++mode) {
            checkins=disposals=cancels=region_calls=0; trace_events.clear(); trace_events.reserve(64);
            // Exercise both an absent optional slot and an available but forbidden query.
            renders.AEGP_GetRenderedRegion=(mode%2==0)?nullptr:+forbidden_region;
            caller_thread=std::this_thread::get_id(); trace_wrong_thread=false;
            startup_frame::Capture capture(options,renders,worlds,Trace);
            active_capture=&capture;worker_release.store(false,std::memory_order_release);
            bool start_failed=false;
            try { capture.Start(1,reinterpret_cast<AEGP_LayerH>(0x4000)); } catch (...) { start_failed=true; }
            Check(start_failed==(mode>=13 && mode<=15));
            if(mode==2 || mode==13) {
                Check(capture.Pending()&&!capture.Done());Check(capture.Cancel()&&!capture.Cancel()&&cancels==1);
                const auto diagnostic=capture.Diagnostic();
                Check(diagnostic.find("callback=PENDING\n")!=std::string::npos &&
                    diagnostic.find("callback_error=")==std::string::npos &&
                    diagnostic.find("callback_on_start_thread=")==std::string::npos &&
                    diagnostic.find("callback_submit_return_published=")==std::string::npos &&
                    diagnostic.find("callback_delivery=")==std::string::npos);
                bool refused=false;try { capture.Release(); } catch (...) { refused=true; }Check(refused);
                std::thread worker(Deliver);worker.join();
            }
            if(mode==18 || mode==19) {
                const auto pending=capture.Diagnostic();
                // The new receipt/order fields are absent until Done's acquire.
                const bool hidden=capture.Pending() && !capture.Done() &&
                    pending.find("callback_delivery=")==std::string::npos &&
                    pending.find("callback_submit_return_published=")==std::string::npos;
                if(mode==18) Deliver();
                else {
                    worker_release.store(true,std::memory_order_release);
                    while(!capture.Done()) std::this_thread::yield();
                    // Consume the published plain fields before joining the
                    // worker; visibility must come from Done, not thread join.
                    const auto observed=capture.Diagnostic();
                    deferred_worker.join();
                    Check(observed.find("callback_delivery=WORKER_RETURN_PUBLISHED\n")!=std::string::npos);
                }
                Check(hidden);
            }
            Check(trace_events.empty() && !trace_wrong_thread); // no callback trace/SDK/IO
            bool copied=false;
            std::string frame;
            try { frame=capture.Copy();copied=true; }
            catch(const std::runtime_error&) {}
            const char* expected_stage[]={"copied","copied","copied","world-type","world-size",
                "world-rowbytes","world-base","receipt-world","callback-error","callback-canceled",
                "callback-id","copied","copied","copy-accepted","copy-accepted","copy-accepted","world-handle","copied",
                "copied","copied","copied"};
            const auto diagnostic=capture.Diagnostic();
            if(capture.Done()) Check(diagnostic.find(std::string("callback_on_start_thread=")+
                ((mode==1||mode==2||mode==13||mode==19)?"NO":"YES")+"\n")!=std::string::npos);
            if(capture.Done()) {
                const bool returned=mode==2||mode==13||mode==18||mode==19;
                Check(diagnostic.find(std::string("callback_submit_return_published=")+
                    (returned?"YES":"NO")+"\n")!=std::string::npos);
                const char* delivery=(mode==1)?"WORKER_RETURN_NOT_PUBLISHED":
                    (mode==2||mode==13||mode==19)?"WORKER_RETURN_PUBLISHED":
                    (mode==18)?"CALLER_AFTER_SUBMIT":"CALLER_DURING_SUBMIT";
                Check(diagnostic.find(std::string("callback_delivery=")+delivery+"\n")!=std::string::npos);
            }
            Check(diagnostic.find(std::string("stage=")+expected_stage[mode]+"\n")!=std::string::npos);
            if(mode==8) Check(diagnostic.find("callback_error=1\n")!=std::string::npos);
            if(mode==3) Check(diagnostic.find("world_type="+std::to_string(AEGP_WorldType_16)+"\n")!=std::string::npos);
            if(mode==4) Check(diagnostic.find("width=65\n")!=std::string::npos);
            if(mode==5) Check(diagnostic.find("rowbytes=255\n")!=std::string::npos);
            if(mode==16) Check(diagnostic.find("sdk_error=0\n")!=std::string::npos &&
                diagnostic.find("receipt=YES\n")!=std::string::npos);
            if(mode==17) Check(capture.OptionsDiagnostic().find("time_error=1\n")!=std::string::npos &&
                diagnostic.find("region_right=")==std::string::npos);
            Check(region_calls==0 && diagnostic.find("region_queried=NO\n")!=std::string::npos);
            if(!start_failed) Check(capture.OptionsDiagnostic().find("requested_world_type="+std::to_string(AEGP_WorldType_8)+"\n")!=std::string::npos);
            Check(copied==(mode<=2 || mode==11 || mode==12 || mode>=17));
            if(copied) { Check(frame.size()==64*48*4);
                for(int y=0;y<48;++y)Check(std::memcmp(frame.data()+y*256,pixels.data()+y*288,256)==0); }
            Check(capture.Release()==(mode!=9 && mode!=11 && mode!=12 && mode!=14));
            Check(disposals==((mode==9||(mode==14||mode==15))?0:1)&&checkins==((mode==8||mode==9||(mode==14||mode==15))?0:1));
            const auto old_checkins=checkins,old_disposals=disposals;capture.Release();
            Check(checkins==old_checkins&&disposals==old_disposals);
            Check(!trace_wrong_thread);
            if (copied) {
                Check(trace_events.size()>=12);
                for(unsigned i=0;i<12;++i) Check(trace_events[i]==i+2);
            }
            for (std::size_t i=0;i<trace_events.size();i+=2)
                Check(i+1<trace_events.size() && trace_events[i+1]==trace_events[i]+1);
        }
        std::cout<<"PASS:21 SDK async frame cases; submit-return publication, same-thread deferred, worker deferred, reentrant refusal, cancellation, world and cleanup refusals; Adobe_calls=0\n";
    } catch(const std::exception& error) { std::cerr<<error.what()<<'\n';return 1; }
}
