





BUILD_DIR = build

SYS_LIB_PATH = /home/jiang/miniconda3/envs/course-eece7398-st-compiler/lib 
LLVM_PASS_LIB = ../loop-unroll/build/LoopUnroll/LoopUnrollPass.so

TARGET_SRC = matmul.cpp
TARGET = $(basename $(TARGET_SRC))
TARGET_WITH_PASS = $(TARGET)_with_pass
TARGET_WITHOUT_PASS = $(TARGET)_without_pass
TARGET_OBJ = $(subst .cpp,.o,$(TARGET_SRC))
TARGET_IR = $(TARGET).ll
TARGET_IR_WITH_PASS = $(TARGET)_with_pass.ll

CC = clang
CLANG = clang
OPT = opt
MKDIR_SAFE = mkdir -p
RM_F = rm -f
RM_RF = rm -rf

.PHONY: all clean run

all: $(BUILD_DIR) $(LLVM_PASS_LIB) $(TARGET_WITH_PASS) $(TARGET_WITHOUT_PASS)

$(TARGET_IR): $(TARGET_SRC)
	@echo "Generating LLVM IR..."
	$(CLANG) -x c++ -O0 -S --stdlib=libc++ -emit-llvm $< -o $@

$(TARGET_IR_WITH_PASS): $(TARGET_IR) $(LLVM_PASS_LIB)
	@echo "Applying custom LLVM pass..."
	$(OPT) -load-pass-plugin=$(LLVM_PASS_LIB) -passes="my-loop-unroll" -S $< -o $@

$(TARGET_WITH_PASS): $(TARGET_IR_WITH_PASS)
	@echo "Compiling target with custom LLVM pass..."
	$(CLANG) $< -o $@ -L$(SYS_LIB_PATH) -lc++ -lc++abi -Wl,-rpath,$(SYS_LIB_PATH)

$(TARGET_WITHOUT_PASS): $(TARGET_IR)
	@echo "Compiling target without custom LLVM pass..."
	$(CLANG) $< -o $@ -L$(SYS_LIB_PATH) -lc++ -lc++abi -Wl,-rpath,$(SYS_LIB_PATH)

run: $(BUILD_DIR) $(TARGET_WITH_PASS) $(TARGET_WITHOUT_PASS)
	@echo "Running target with custom LLVM pass..."
	time ./$(TARGET_WITH_PASS)
	@echo "Running target without custom LLVM pass..."
	time ./$(TARGET_WITHOUT_PASS)

$(BUILD_DIR):
	$(MKDIR_SAFE) $(BUILD_DIR)

clean:
	$(RM_RF) $(BUILD_DIR)
	$(RM_F) $(TARGET_WITH_PASS) $(TARGET_WITHOUT_PASS) $(TARGET_IR) $(TARGET_IR_WITH_PASS)




# all:
# 	clang -x c++ -O0 -S --stdlib=libc++ -emit-llvm matmul.cpp -o matmul.ll
# 	opt -load-pass-plugin=../loop-unroll/build/LoopUnroll/LoopUnrollPass.so -passes="my-loop-unroll" -S matmul.ll -o matmul.pass.ll
# 	clang -x c++ matmul.pass.ll -o matmul.pass
# 	clang -x c++ matmul.ll -o matmul

# clean:
# 	rm -f matmul.ll matmul.pass.ll matmul.pass matmul

