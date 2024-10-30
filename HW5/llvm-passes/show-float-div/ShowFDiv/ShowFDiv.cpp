#include "llvm/Pass.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Instruction.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"
using namespace llvm;

#define __FILE_NAME__ (strrchr(__FILE__, '/') ? strrchr(__FILE__, '/') + 1 : __FILE__)
#define __HERE__ __FILE_NAME__ << ":" << __LINE__

namespace {

struct SkeletonPass : public PassInfoMixin<SkeletonPass> {
    PreservedAnalyses run(Module &M, ModuleAnalysisManager &AM) {
        bool modified = false; // Track if any modifications were made
        for (auto &F : M.functions()) {

            // Get the function to call from our runtime library.
            LLVMContext &Ctx = F.getContext();
            std::vector<Type*> paramTypes = {Type::getFloatTy(Ctx), Type::getFloatTy(Ctx), Type::getFloatTy(Ctx)};
            Type *retType = Type::getVoidTy(Ctx);
            FunctionType *logFuncType = FunctionType::get(retType, paramTypes, false);
            FunctionCallee logFunc = F.getParent()->getOrInsertFunction("logfdiv", logFuncType);

            for (auto &B : F) {
                for (auto &I : B) {
                    if (auto *op = dyn_cast<BinaryOperator>(&I)) {
                        if (op->getOpcode() == llvm::Instruction::FDiv) {

                            errs() << "\n";
                            errs() << __HERE__ << ": Found FDiv operator: " << *op << "\n";
                            I.print(errs());
                            errs() << "\n";
                            errs() << "OpcodeName: " << op->getOpcodeName() << "\n";
                            errs() << "\n";

                            // create a builder based on the current instruction
                            IRBuilder<> builder(op);

                            // Insert *after* `op`.
                            builder.SetInsertPoint(&B, ++builder.GetInsertPoint());

                            // Insert a call to the pin function.
                            Value* op_val_float = builder.CreateFPCast(op, builder.getFloatTy());
                            Value* lhs_float = builder.CreateFPCast(op->getOperand(0), builder.getFloatTy());
                            Value* rhs_float = builder.CreateFPCast(op->getOperand(1), builder.getFloatTy());

                            Value* args[] = {op_val_float, lhs_float, rhs_float};
                            builder.CreateCall(logFunc, args);

                            modified = true; // Mark that we modified the function
                        }
                    }
                }
            }

        }
        return modified ? PreservedAnalyses::none() : PreservedAnalyses::all();
    }
};

}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
    return {
        .APIVersion = LLVM_PLUGIN_API_VERSION,
        .PluginName = "Skeleton pass",
        .PluginVersion = "v0.1",
        .RegisterPassBuilderCallbacks = [](PassBuilder &PB) {
            PB.registerPipelineStartEPCallback(
                [](ModulePassManager &MPM, OptimizationLevel Level) {
                    MPM.addPass(SkeletonPass());
                });
        }
    };
}
