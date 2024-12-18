#include "llvm/Pass.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"
using namespace llvm;

namespace {

struct SkeletonPass : public PassInfoMixin<SkeletonPass> {
    PreservedAnalyses run(Module &M, ModuleAnalysisManager &AM) {
        for (auto &F : M.functions()) {

            // Get the function to call from our runtime library.
            LLVMContext &Ctx = F.getContext();
            std::vector<Type*> paramTypes = {Type::getInt32Ty(Ctx)};
            Type *retType = Type::getVoidTy(Ctx);
            FunctionType *logFuncType = FunctionType::get(retType, paramTypes, false);
            FunctionCallee logFunc =
                F.getParent()->getOrInsertFunction("logop", logFuncType);

            for (auto &B : F) {
                for (auto &I : B) {
                    if (auto *op = dyn_cast<BinaryOperator>(&I)) {
                        // Insert *after* `op`.
                        IRBuilder<> builder_after(op);
                        builder_after.SetInsertPoint(&B, ++builder_after.GetInsertPoint());

                        // Insert a call to our function.
                        Value* args[] = {op};
                        builder_after.CreateCall(logFunc, args);

                        // Insert *before* `op`
                        IRBuilder<> builder(op);

                        // Make a multiply with the same operands as `op`.
                        Value *lhs = op->getOperand(0);
                        Value *rhs = op->getOperand(1);
                        Value *mul = builder.CreateMul(lhs, rhs);

                        // Everywhere the old instruction was used as an
                        // operand, use our new multiply instruction instead.
                        for (auto &U : op->uses()) {
                          // A User is anything with operands.
                          User *user = U.getUser();
                          user->setOperand(U.getOperandNo(), mul);
                        }

                        return PreservedAnalyses::none();
                    }
                }
            }

        }
        return PreservedAnalyses::all();
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
