#include "llvm/IR/Function.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/PassManager.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Transforms/Utils/UnrollLoop.h"
#include "llvm/Analysis/LoopInfo.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

#define __FILE_NAME__ (strrchr(__FILE__, '/') ? strrchr(__FILE__, '/') + 1 : __FILE__)
#define __HERE__ __FILE_NAME__ << ":" << __LINE__

namespace {

struct LoopUnrollPass : public PassInfoMixin<LoopUnrollPass> {
    PreservedAnalyses run(Function &F, FunctionAnalysisManager &FAM) {
        // Get loop analysis.
        LoopAnalysis::Result &LI = FAM.getResult<LoopAnalysis>(F);

        bool modified = false;
        for (Loop *L : LI) {
            // Ensure the loop is in simplified form.
            if (L->isLoopSimplifyForm() && L->getLoopLatch()) {
                // Unroll the loop by a factor of 2.
                modified |= UnrollLoop(L, {2, /*AllowRuntime=*/false, /*AllowExpensiveTripCount=*/false});
            }
        }

        return modified ? PreservedAnalyses::none() : PreservedAnalyses::all();
    }
};

}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
    return {
        .APIVersion = LLVM_PLUGIN_API_VERSION, 
        .PluginName = "LoopUnrollPass", 
        .PluginVersion = LLVM_VERSION_STRING,
        .RegisterPassBuilderCallbacks = [](PassBuilder &PB) {
            // Register the pass with the "function-level" optimization pipeline.
            PB.registerPipelineParsingCallback(
                [](StringRef Name, FunctionPassManager &FPM,
                    ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "my-loop-unroll") {
                        FPM.addPass(LoopUnrollPass());
                        return true;
                    }
                    return false;
                });
        }};
}
