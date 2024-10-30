BUILD_DIR = build

LLVM_PASS_LIB = $(BUILD_DIR)/LoopUnroll/LoopUnrollPass.so

TARGET_SRC = example.c
TARGET = $(basename $(TARGET_SRC))
TARGET_OBJ = $(subst .c,.o,$(TARGET_SRC))

CC = clang
CLANG = clang
MKDIR_SAFE = mkdir -p
RM_F = rm -f
RM_RF = rm -rf

.PHONY: all clean run

all: $(BUILD_DIR) $(TARGET)

$(LLVM_PASS_LIB): LoopUnroll/LoopUnroll.cpp LoopUnroll/CMakeLists.txt CMakeLists.txt
	@echo "Building LLVM Pass..."
	@make -C . $(BUILD_DIR)
	cd $(BUILD_DIR) && cmake .. && make

$(TARGET): $(TARGET_SRC) $(LLVM_PASS_LIB)
	@echo "Compiling target..."
	$(CLANG) -fpass-plugin=$(LLVM_PASS_LIB) -c $<
	$(CC) $(TARGET_OBJ) -o $(TARGET)
	$(RM_F) $(TARGET_OBJ)

run: $(BUILD_DIR) $(TARGET)
	@echo "Running target..."
	./$(TARGET)

$(BUILD_DIR):
	$(MKDIR_SAFE) $(BUILD_DIR)

clean:
	$(RM_RF) $(BUILD_DIR)
	$(RM_F) $(TARGET)
