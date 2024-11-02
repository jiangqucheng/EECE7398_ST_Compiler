#include "llvm/IR/Function.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/PassManager.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Transforms/Utils/UnrollLoop.h"
#include "llvm/Analysis/LoopInfo.h"
#include "llvm/Support/raw_ostream.h"

#include "llvm/IR/Function.h"
#include "llvm/IR/PassManager.h"
#include "llvm/IR/Instructions.h"
#include "llvm/Transforms/Utils/UnrollLoop.h"
#include "llvm/Analysis/LoopInfo.h"
#include "llvm/Analysis/ScalarEvolution.h"
#include "llvm/IR/Dominators.h"
#include "llvm/Analysis/AssumptionCache.h"
#include "llvm/Analysis/TargetTransformInfo.h"


using namespace llvm;

#define __FILE_NAME__ (strrchr(__FILE__, '/') ? strrchr(__FILE__, '/') + 1 : __FILE__)
#define __HERE__ __FILE_NAME__ << ":" << __LINE__

namespace {

struct LoopUnrollPass : public PassInfoMixin<LoopUnrollPass> {
    PreservedAnalyses run(Function &F, FunctionAnalysisManager &FAM) {
        errs() << __HERE__ << "Running Loop Unroll Pass on function: " << F.getName() << "\n";

        // Get loop analysis.
        LoopAnalysis::Result &LI = FAM.getResult<LoopAnalysis>(F);

        // Get required analyses for UnrollLoop.
        // auto &LI = FAM.getResult<LoopAnalysis>(F);
        auto &SE = FAM.getResult<ScalarEvolutionAnalysis>(F);
        auto &DT = FAM.getResult<DominatorTreeAnalysis>(F);
        auto &AC = FAM.getResult<AssumptionAnalysis>(F);
        auto &TTI = FAM.getResult<TargetIRAnalysis>(F);
        // auto &ORE = FAM.getResult<OptimizationRemarkEmitterAnalysis>(F);

        bool modified = false;
        for (Loop *L : LI) {
            errs() << __HERE__ << "Found loop: " << *L << "\n";

            // Ensure the loop is in simplified form.
            if (L->isLoopSimplifyForm() && L->getLoopLatch()) {
                errs() << __HERE__ << "Unrolling loop!\n";

                // Configure unroll options
                UnrollLoopOptions ULO;
                ULO.Count = 2; // Unroll factor
                ULO.Runtime = false;
                ULO.AllowExpensiveTripCount = false;
                
                modified |= UnrollLoop(L, ULO, &LI, &SE, &DT, &AC, &TTI, nullptr, false, nullptr) != LoopUnrollResult::Unmodified;
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
            errs() << "Registering LoopUnrollPass\n";
            // Register the pass with the "function-level" optimization pipeline.
            PB.registerPipelineParsingCallback(
                [](StringRef Name, FunctionPassManager &FPM,
                    ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "my-loop-unroll") {
                        errs() << "Adding my-loop-unroll to the pipeline\n";
                        FPM.addPass(LoopUnrollPass());
                        return true;
                    }
                    return false;
                });
        }};
}
