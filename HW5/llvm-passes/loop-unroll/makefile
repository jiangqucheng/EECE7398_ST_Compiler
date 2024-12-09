BUILD_DIR = build

LLVM_PASS_LIB = $(BUILD_DIR)/LoopUnroll/LoopUnrollPass.so

TARGET_SRC = example.c
TARGET = $(basename $(TARGET_SRC))
TARGET_WITH_PASS = $(TARGET)_unrolled
TARGET_WITHOUT_PASS = $(TARGET)_orig
TARGET_OBJ = $(subst .c,.o,$(TARGET_SRC))
TARGET_IR = $(subst .c,.ll,$(TARGET_SRC))
TARGET_IR_WITH_PASS = $(subst .c,.pass.ll,$(TARGET_SRC))

CC = clang
CLANG = clang
OPT = opt
MKDIR_SAFE = mkdir -p
RM_F = rm -f
RM_RF = rm -rf

.PHONY: all clean run

all: $(BUILD_DIR) $(LLVM_PASS_LIB) $(TARGET_WITH_PASS) $(TARGET_WITHOUT_PASS)


$(LLVM_PASS_LIB): LoopUnroll/LoopUnroll.cpp LoopUnroll/CMakeLists.txt CMakeLists.txt
	@echo "Building LLVM Pass..."
	@make -C . $(BUILD_DIR)
	cd $(BUILD_DIR) && cmake .. && make


$(TARGET_IR): $(TARGET_SRC)
	@echo "Generating LLVM IR..."
	$(CLANG) -O0 -S -emit-llvm $< -o $@

$(TARGET_IR_WITH_PASS): $(TARGET_IR) $(LLVM_PASS_LIB)
	@echo "Applying custom LLVM pass..."
	$(OPT) -load-pass-plugin=$(LLVM_PASS_LIB) -passes="my-loop-unroll" -S $< -o $@

$(TARGET_WITH_PASS): $(TARGET_IR_WITH_PASS)
	@echo "Compiling target with custom LLVM pass..."
	$(CLANG) $< -o $@

$(TARGET_WITHOUT_PASS): $(TARGET_IR)
	@echo "Compiling target without custom LLVM pass..."
	$(CLANG) $< -o $@

run: $(BUILD_DIR) $(TARGET_WITH_PASS) $(TARGET_WITHOUT_PASS)
	@echo "\n"
	@echo "Running target with custom LLVM pass..."
	time ./$(TARGET_WITH_PASS)
	@echo "\n\n"
	@echo "Running target without custom LLVM pass..."
	time ./$(TARGET_WITHOUT_PASS)
	@echo "\n"

$(BUILD_DIR):
	$(MKDIR_SAFE) $(BUILD_DIR)

clean_ll:
	$(RM_F) $(TARGET_IR) $(TARGET_IR_WITH_PASS) $(TARGET_WITH_PASS) $(TARGET_WITHOUT_PASS)

clean:
	$(RM_RF) $(BUILD_DIR)
	$(RM_F) $(TARGET_WITH_PASS) $(TARGET_WITHOUT_PASS) $(TARGET_IR) $(TARGET_IR_WITH_PASS)
