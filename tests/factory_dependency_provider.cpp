#include <cstdint>
#ifndef AEHL_DEPENDENCY_VERSION
#define AEHL_DEPENDENCY_VERSION 0x4145484c00000003ULL
#endif
#ifndef AEHL_PROVIDER_ID
#define AEHL_PROVIDER_ID 30
#endif
namespace { void (*event)(int) noexcept = nullptr; }
extern "C" std::uint64_t AEHL_OwnedDependencyVersion() noexcept { return AEHL_DEPENDENCY_VERSION; }
#ifndef AEHL_DEPENDENCY_MISSING_TEARDOWN
extern "C" void AEHL_OwnedDependencyTeardown() noexcept { if(event) event(AEHL_PROVIDER_ID); }
#endif
extern "C" void AEHL_TestDependencyEvent(void (*f)(int) noexcept) noexcept { event=f; }
__attribute__((destructor)) static void OnUnload() { if(event) event(AEHL_PROVIDER_ID+1); }
