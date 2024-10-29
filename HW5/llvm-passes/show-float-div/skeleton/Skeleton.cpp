#include "llvm/Pass.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"
using namespace llvm;

#define __HERE__ __FILE__ << ":" << __LINE__

namespace {

struct SkeletonPass : public PassInfoMixin<SkeletonPass> {
    PreservedAnalyses run(Module &M, ModuleAnalysisManager &AM) {
        for (auto &F : M.functions()) {

            // Get the function to call from our runtime library.
            LLVMContext &Ctx = F.getContext();
            std::vector<Type*> paramTypes = {Type::getInt32Ty(Ctx)};
            Type *retType = Type::getVoidTy(Ctx);
            FunctionType *logFuncType = FunctionType::get(retType, paramTypes, false);
            FunctionCallee logFunc = F.getParent()->getOrInsertFunction("logop", logFuncType);

            for (auto &B : F) {
                for (auto &I : B) {
                    if (auto *op = dyn_cast<BinaryOperator>(&I)) {

                        errs() << "\n";
                        errs() << __HERE__ << ": Found binary operator: " << *op << "\n";
                        I.print(errs());
                        errs() << "\n";
                        errs() << "\n";


                        // Insert *before* `op`
                        IRBuilder<> builder(op);

                        // Make a multiply with the same operands as `op1`.
                        Value *lhs = op->getOperand(0);
                        Value *rhs = op->getOperand(1);
                        Value *mul = builder.CreateNSWMul(lhs, rhs);

                        // Everywhere the old instruction was used as an
                        // operand, use our new multiply instruction instead.
                        for (auto &U : op->uses()) {
                          // A User is anything with operands.
                          User *user = U.getUser();
                          user->setOperand(U.getOperandNo(), mul);
                        }

                        // Update op to the modified instruction.
                        op = dyn_cast<BinaryOperator>(mul);

                        // Insert *after* `op`.
                        builder.SetInsertPoint(&B, ++builder.GetInsertPoint());

                        // Insert a call to our function.
                        Value* args[] = {op};
                        builder.CreateCall(logFunc, args);

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
