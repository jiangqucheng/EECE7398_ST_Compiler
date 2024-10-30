#include "llvm/Pass.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Instruction.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"
using namespace llvm;

#define __HERE__ __FILE__ << ":" << __LINE__

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

                        errs() << "\n";
                        errs() << __HERE__ << ": Found binary operator: " << *op << "\n";
                        I.print(errs());
                        errs() << "\n";
                        errs() << "Opcode: " << op->getOpcode() << "\n";
                        errs() << "OpcodeName: " << op->getOpcodeName() << "\n";
                        errs() << (op->getOpcode() == llvm::Instruction::Add)
                               << (op->getOpcode() == llvm::Instruction::FAdd)
                               << (op->getOpcode() == llvm::Instruction::Sub)
                               << (op->getOpcode() == llvm::Instruction::FSub)
                               << (op->getOpcode() == llvm::Instruction::Mul)
                               << (op->getOpcode() == llvm::Instruction::FMul)
                               << (op->getOpcode() == llvm::Instruction::FDiv) << "\n";
                        errs() << "\n";

                        if (op->getOpcode() == llvm::Instruction::FDiv) {
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
