#pragma once
#include "AEConfig.h"
#include "AE_GeneralPlug.h"
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <string>
#include <thread>

namespace startup_frame {
// SDK callbacks may arrive on a worker or inline. They only publish plain data.
// The caller owns this object and all suites until completion on the main thread.
class Capture {
    const AEGP_LayerRenderOptionsSuite2& options_;
    const AEGP_RenderSuite5& render_;
    const AEGP_WorldSuite3& world_;
    AEGP_LayerRenderOptionsH option_ = nullptr;
    AEGP_FrameReceiptH receipt_ = nullptr;
    AEGP_AsyncRequestId request_ = 0, callback_id_ = 0;
    A_Err callback_error_ = 1;
    A_Boolean canceled_ = TRUE;
    std::thread::id start_thread_;
    bool callback_on_start_thread_=false;
    std::atomic<bool> done_{false};
    bool starting_ = false, sent_ = false, accepted_ = false, option_owned_ = false, cancel_sent_ = false;
    const char* stage_ = "constructed";
    A_Err last_error_ = 0;
    A_long observed_width_ = 0, observed_height_ = 0;
    AEGP_WorldType observed_type_ = AEGP_WorldType_NONE;
    std::string option_facts_;
    A_LRect region_{};
    A_Err region_error_=1;
    bool region_queried_=false;
    void ReadOptions() {
        A_Time time{},step{}; AEGP_WorldType type=AEGP_WorldType_NONE;
        A_short x=0,y=0; AEGP_MatteMode matte{};
        const auto time_error=options_.AEGP_GetTime(option_,&time);
        const auto step_error=options_.AEGP_GetTimeStep(option_,&step);
        const auto type_error=options_.AEGP_GetWorldType(option_,&type);
        const auto downsample_error=options_.AEGP_GetDownsampleFactor(option_,&x,&y);
        const auto matte_error=options_.AEGP_GetMatteMode(option_,&matte);
        option_facts_="AEHL-CAL-OPTIONS-1\ntime_error="+std::to_string(time_error)+
            "\ntime="+std::to_string(time.value)+"/"+std::to_string(time.scale)+
            "\nstep_error="+std::to_string(step_error)+"\nstep="+std::to_string(step.value)+"/"+std::to_string(step.scale)+
            "\ntype_error="+std::to_string(type_error)+"\nrequested_world_type="+std::to_string(type)+
            "\ndownsample_error="+std::to_string(downsample_error)+"\ndownsample_x="+std::to_string(x)+
            "\ndownsample_y="+std::to_string(y)+"\nmatte_error="+std::to_string(matte_error)+
            "\nmatte="+std::to_string(matte)+"\n";
    }
    static void Need(bool value) { if (!value) throw std::runtime_error("frame capture refused"); }
    void Check(const char* stage, bool okay) { stage_=stage; Need(okay); }
    void SDK(const char* stage, A_Err error) { stage_=stage; last_error_=error; Need(error==0); }
    static A_Err Ready(AEGP_AsyncRequestId id, A_Boolean canceled, A_Err error,
                       AEGP_FrameReceiptH receipt, AEGP_AsyncFrameRequestRefcon context) noexcept {
        auto* self = reinterpret_cast<Capture*>(context);
        self->callback_id_ = id; self->canceled_ = canceled;
        self->callback_error_ = error; self->receipt_ = receipt;
        self->callback_on_start_thread_=std::this_thread::get_id()==self->start_thread_;
        self->done_.store(true, std::memory_order_release);
        return 0; // No SDK/filesystem/project operation on the callback thread.
    }
public:
    bool cleanup_ok = true;
    A_u_long rowbytes = 0;
    Capture(const AEGP_LayerRenderOptionsSuite2& options, const AEGP_RenderSuite5& render,
            const AEGP_WorldSuite3& world) : options_(options), render_(render), world_(world) {
        Need(options_.AEGP_NewFromLayer && options_.AEGP_Dispose && options_.AEGP_SetTime &&
            options_.AEGP_SetTimeStep && options_.AEGP_SetWorldType && options_.AEGP_SetDownsampleFactor &&
            options_.AEGP_SetMatteMode && options_.AEGP_GetTime && options_.AEGP_GetTimeStep &&
            options_.AEGP_GetWorldType && options_.AEGP_GetDownsampleFactor && options_.AEGP_GetMatteMode &&
            render_.AEGP_GetRenderedRegion && render_.AEGP_RenderAndCheckoutLayerFrame_Async &&
            render_.AEGP_CancelAsyncRequest && render_.AEGP_CheckinFrame && render_.AEGP_GetReceiptWorld &&
            world_.AEGP_GetType && world_.AEGP_GetSize && world_.AEGP_GetRowBytes && world_.AEGP_GetBaseAddr8);
        static_assert(sizeof(PF_Pixel8) == 4 && offsetof(PF_Pixel8, alpha) == 0 &&
            offsetof(PF_Pixel8, red) == 1 && offsetof(PF_Pixel8, green) == 2 && offsetof(PF_Pixel8, blue) == 3);
    }
    Capture(const Capture&) = delete;
    Capture& operator=(const Capture&) = delete;
    // Do not destroy a sent object before Ready: its callback retains context.
    bool Pending() const { return sent_ && (!done_.load(std::memory_order_acquire) || starting_); }
    bool Done() const { return !starting_ && done_.load(std::memory_order_acquire); }
    const std::string& OptionsDiagnostic() const { return option_facts_; }
    std::string Diagnostic() const {
        // Called only on the main thread. Never read callback data before acquire.
        std::string text=std::string("AEHL-CAL-FRAME-DIAG-1\nstage=")+stage_+
            "\nsdk_error="+std::to_string(last_error_)+"\n";
        if (Done()) text+=std::string("callback=READY\ncanceled=")+(canceled_?"YES":"NO")+
            "\ncallback_error="+std::to_string(callback_error_)+"\nrequest_id_equal="+
            (callback_id_==request_?"YES":"NO")+"\nreceipt="+(receipt_?"YES":"NO")+
            "\ncallback_on_start_thread="+(callback_on_start_thread_?"YES":"NO")+"\n";
        else text+="callback=PENDING\n";
        text+=std::string("region_queried=")+(region_queried_?"YES":"NO")+"\n";
        if(region_queried_) {
            text+="region_error="+std::to_string(region_error_)+"\n";
            if(region_error_==0) text+="region_left="+std::to_string(region_.left)+
                "\nregion_top="+std::to_string(region_.top)+"\nregion_right="+std::to_string(region_.right)+
                "\nregion_bottom="+std::to_string(region_.bottom)+"\n";
        }
        return text+"world_type="+std::to_string(observed_type_)+"\nwidth="+
            std::to_string(observed_width_)+"\nheight="+std::to_string(observed_height_)+
            "\nrowbytes="+std::to_string(rowbytes)+"\n";
    }
    void Start(AEGP_PluginID id, AEGP_LayerH layer) {
        Check("start-state",!sent_ && !option_);
        const auto create_error=options_.AEGP_NewFromLayer(id, layer, &option_);
        SDK("new-options",create_error); Check("options-handle",option_!=nullptr); option_owned_=true;
        SDK("set-time",options_.AEGP_SetTime(option_, {1,24}));
        SDK("set-time-step",options_.AEGP_SetTimeStep(option_, {1,24}));
        SDK("set-world-type",options_.AEGP_SetWorldType(option_,AEGP_WorldType_8));
        SDK("set-downsample",options_.AEGP_SetDownsampleFactor(option_,1,1));
        SDK("set-matte",options_.AEGP_SetMatteMode(option_,AEGP_MatteMode_STRAIGHT));
        ReadOptions(); // Read-only facts; no acceptance or render-option changes.
        start_thread_=std::this_thread::get_id();
        starting_ = true; sent_ = true; // before an inline callback/reentrant idle
        const auto error = render_.AEGP_RenderAndCheckoutLayerFrame_Async(option_, Ready,
            reinterpret_cast<AEGP_AsyncFrameRequestRefcon>(this), &request_);
        starting_ = false;
        // Ambiguous error after submission must retain this context until callback/host shutdown.
        SDK("submit",error); Check("request-handle",request_!=0);
        accepted_=true;
        stage_="submitted";
    }
    bool Cancel() {
        if (cancel_sent_ || !request_ || Done()) return false;
        cancel_sent_ = true;
        return render_.AEGP_CancelAsyncRequest(request_) == 0;
    }
    std::string Copy() {
        Check("copy-accepted",accepted_); Check("callback-ready",Done());
        Check("callback-id",callback_id_==request_); Check("callback-canceled",!canceled_);
        Check("callback-error",callback_error_==0); Check("callback-receipt",receipt_!=nullptr);
        region_error_=render_.AEGP_GetRenderedRegion(receipt_,&region_); region_queried_=true;
        AEGP_WorldH world = nullptr; AEGP_WorldType type = AEGP_WorldType_NONE;
        A_long width = 0, height = 0; PF_Pixel8* pixels = nullptr;
        SDK("receipt-world",render_.AEGP_GetReceiptWorld(receipt_,&world)); Check("world-handle",world!=nullptr);
        SDK("world-type-api",world_.AEGP_GetType(world,&type)); observed_type_=type; Check("world-type",type==AEGP_WorldType_8);
        SDK("world-size-api",world_.AEGP_GetSize(world,&width,&height)); observed_width_=width; observed_height_=height;
        Check("world-size",width==64 && height==48);
        SDK("world-rowbytes-api",world_.AEGP_GetRowBytes(world,&rowbytes)); Check("world-rowbytes",rowbytes>=256 && rowbytes<=65536);
        SDK("world-base-api",world_.AEGP_GetBaseAddr8(world,&pixels)); Check("world-base",pixels!=nullptr);
        std::string packed(64 * 48 * 4, '\0');
        for (std::size_t y = 0; y < 48; ++y) std::memcpy(packed.data() + y * 256,
            reinterpret_cast<const unsigned char*>(pixels) + y * rowbytes, 256);
        stage_="copied";
        return packed; // remove row padding only; no channel/depth/color conversion
    }
    bool Release() {
        Need(!Pending());
        if (receipt_) {
            // A failure callback with nonnull data has no established checkout ownership.
            if (callback_error_ != 0 || canceled_) { cleanup_ok = false; return false; }
            auto receipt = receipt_; receipt_ = nullptr;
            if (render_.AEGP_CheckinFrame(receipt)) cleanup_ok = false;
        }
        if (option_ && !option_owned_) { cleanup_ok=false;return false; }
        if (option_) { auto option = option_; option_ = nullptr;
            if (options_.AEGP_Dispose(option)) cleanup_ok = false; }
        return cleanup_ok;
    }
};
} // namespace startup_frame
