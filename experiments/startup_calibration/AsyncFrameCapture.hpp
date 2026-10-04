#pragma once
#include "AEConfig.h"
#include "AE_GeneralPlug.h"
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <string>

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
    std::atomic<bool> done_{false};
    bool starting_ = false, sent_ = false, accepted_ = false, option_owned_ = false, cancel_sent_ = false;
    static void Need(bool value) { if (!value) throw std::runtime_error("frame capture refused"); }
    static A_Err Ready(AEGP_AsyncRequestId id, A_Boolean canceled, A_Err error,
                       AEGP_FrameReceiptH receipt, AEGP_AsyncFrameRequestRefcon context) noexcept {
        auto* self = reinterpret_cast<Capture*>(context);
        self->callback_id_ = id; self->canceled_ = canceled;
        self->callback_error_ = error; self->receipt_ = receipt;
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
            options_.AEGP_SetMatteMode && render_.AEGP_RenderAndCheckoutLayerFrame_Async &&
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
    void Start(AEGP_PluginID id, AEGP_LayerH layer) {
        Need(!sent_ && !option_);
        const auto create_error=options_.AEGP_NewFromLayer(id, layer, &option_);
        Need(create_error == 0 && option_); option_owned_=true;
        Need(options_.AEGP_SetTime(option_, {1, 24}) == 0 && options_.AEGP_SetTimeStep(option_, {1, 24}) == 0 &&
            options_.AEGP_SetWorldType(option_, AEGP_WorldType_8) == 0 &&
            options_.AEGP_SetDownsampleFactor(option_, 1, 1) == 0 &&
            options_.AEGP_SetMatteMode(option_, AEGP_MatteMode_STRAIGHT) == 0);
        starting_ = true; sent_ = true; // before an inline callback/reentrant idle
        const auto error = render_.AEGP_RenderAndCheckoutLayerFrame_Async(option_, Ready,
            reinterpret_cast<AEGP_AsyncFrameRequestRefcon>(this), &request_);
        starting_ = false;
        // Ambiguous error after submission must retain this context until callback/host shutdown.
        Need(error == 0 && request_ != 0);
        accepted_=true;
    }
    bool Cancel() {
        if (cancel_sent_ || !request_ || Done()) return false;
        cancel_sent_ = true;
        return render_.AEGP_CancelAsyncRequest(request_) == 0;
    }
    std::string Copy() {
        Need(accepted_ && Done() && callback_id_ == request_ && !canceled_ && callback_error_ == 0 && receipt_);
        AEGP_WorldH world = nullptr; AEGP_WorldType type = AEGP_WorldType_NONE;
        A_long width = 0, height = 0; PF_Pixel8* pixels = nullptr;
        Need(render_.AEGP_GetReceiptWorld(receipt_, &world) == 0 && world &&
            world_.AEGP_GetType(world, &type) == 0 && type == AEGP_WorldType_8 &&
            world_.AEGP_GetSize(world, &width, &height) == 0 && width == 64 && height == 48 &&
            world_.AEGP_GetRowBytes(world, &rowbytes) == 0 && rowbytes >= 256 && rowbytes <= 65536 &&
            world_.AEGP_GetBaseAddr8(world, &pixels) == 0 && pixels);
        std::string packed(64 * 48 * 4, '\0');
        for (std::size_t y = 0; y < 48; ++y) std::memcpy(packed.data() + y * 256,
            reinterpret_cast<const unsigned char*>(pixels) + y * rowbytes, 256);
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
