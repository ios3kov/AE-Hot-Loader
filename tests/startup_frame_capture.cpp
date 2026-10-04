// Actual SDK adapter; only our fake host callbacks run in this executable.
#include "../experiments/startup_calibration/AsyncFrameCapture.hpp"
#include "../experiments/startup_calibration/MarkerCore.hpp"
#include <iostream>
#include <thread>
#include <vector>
namespace {
int mode=0,checkins=0,disposals=0,cancels=0;
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
            *out=mode==15?nullptr:option; return mode>=14?1:0; };
        options.AEGP_Dispose=[](AEGP_LayerRenderOptionsH h)->A_Err { Check(h==option);++disposals;return mode==12?1:0; };
        options.AEGP_SetTime=[](AEGP_LayerRenderOptionsH,A_Time t)->A_Err { Check(t.value==1&&t.scale==24);return 0; };
        options.AEGP_SetTimeStep=options.AEGP_SetTime; options.AEGP_SetWorldType=Stub;
        options.AEGP_SetDownsampleFactor=Stub; options.AEGP_SetMatteMode=Stub;
        renders.AEGP_RenderAndCheckoutLayerFrame_Async=[](AEGP_LayerRenderOptionsH,
            AEGP_AsyncFrameReadyCallback fn,AEGP_AsyncFrameRequestRefcon arg,AEGP_AsyncRequestId* out)->A_Err {
            callback=fn;context=arg;*out=5;
            if(mode==1) { std::thread worker(Deliver);worker.join(); }
            else if(mode!=2 && mode!=13) Deliver();
            return mode==13?1:0; };
        renders.AEGP_CancelAsyncRequest=[](AEGP_AsyncRequestId id)->A_Err { Check(id==5);++cancels;return 0; };
        renders.AEGP_CheckinFrame=[](AEGP_FrameReceiptH h)->A_Err { Check(h==receipt);++checkins;return mode==11?1:0; };
        renders.AEGP_GetReceiptWorld=[](AEGP_FrameReceiptH,AEGP_WorldH* out)->A_Err {
            *out=reinterpret_cast<AEGP_WorldH>(0x3000);return mode==7?1:0; };
        worlds.AEGP_GetType=[](AEGP_WorldH,AEGP_WorldType* out)->A_Err { *out=mode==3?AEGP_WorldType_16:AEGP_WorldType_8;return 0; };
        worlds.AEGP_GetSize=[](AEGP_WorldH,A_long* w,A_long* h)->A_Err { *w=mode==4?65:64;*h=48;return 0; };
        worlds.AEGP_GetRowBytes=[](AEGP_WorldH,A_u_long* out)->A_Err { *out=mode==5?255:288;return 0; };
        worlds.AEGP_GetBaseAddr8=[](AEGP_WorldH,PF_Pixel8** out)->A_Err { *out=mode==6?nullptr:reinterpret_cast<PF_Pixel8*>(pixels.data());return 0; };
        Check(startup_marker::Render(pixels.data(),64,48,288,123));
        for (mode=0;mode<16;++mode) {
            checkins=disposals=cancels=0;
            startup_frame::Capture capture(options,renders,worlds);
            bool start_failed=false;
            try { capture.Start(1,reinterpret_cast<AEGP_LayerH>(0x4000)); } catch (...) { start_failed=true; }
            Check(start_failed==(mode>=13));
            if(mode==2 || mode==13) {
                Check(capture.Pending()&&!capture.Done());Check(capture.Cancel()&&!capture.Cancel()&&cancels==1);
                bool refused=false;try { capture.Release(); } catch (...) { refused=true; }Check(refused);
                std::thread worker(Deliver);worker.join();
            }
            bool copied=false;
            std::string frame;
            try { frame=capture.Copy();copied=true; }
            catch(const std::runtime_error&) {}
            Check(copied==(mode<=2 || mode==11 || mode==12));
            if(copied) { Check(frame.size()==64*48*4);
                for(int y=0;y<48;++y)Check(std::memcmp(frame.data()+y*256,pixels.data()+y*288,256)==0); }
            Check(capture.Release()==(mode!=9 && mode!=11 && mode!=12 && mode!=14));
            Check(disposals==((mode==9||mode>=14)?0:1)&&checkins==((mode==8||mode==9||mode>=14)?0:1));
            const auto old_checkins=checkins,old_disposals=disposals;capture.Release();
            Check(checkins==old_checkins&&disposals==old_disposals);
        }
        std::cout<<"PASS:16 SDK async frame cases; inline/worker/delayed callbacks, cancellation, world and cleanup refusals; Adobe_calls=0\n";
    } catch(const std::exception& error) { std::cerr<<error.what()<<'\n';return 1; }
}
