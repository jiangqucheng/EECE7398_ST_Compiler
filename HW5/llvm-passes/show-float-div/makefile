BUILD_DIR = build

RTLIB_SOURCE = rtlib.c
RTLIB_LIB_NAME = $(basename $(RTLIB_SOURCE))
RTLIB_LIB_FILE = $(BUILD_DIR)/lib$(RTLIB_LIB_NAME).so

LLVM_PASS_LIB = $(BUILD_DIR)/ShowFDiv/ShowFDivPass.so

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

$(LLVM_PASS_LIB): ShowFDiv/ShowFDiv.cpp ShowFDiv/CMakeLists.txt CMakeLists.txt
	@echo "Building LLVM Pass..."
	@make -C . $(BUILD_DIR)
	cd $(BUILD_DIR) && cmake .. && make

$(RTLIB_LIB_FILE): $(RTLIB_SOURCE)
	@echo "Building RTLib..."
	@make -C . $(BUILD_DIR)
	$(CC) -fPIC -shared $< -o $(RTLIB_LIB_FILE)

$(TARGET): $(TARGET_SRC) $(RTLIB_LIB_FILE) $(LLVM_PASS_LIB)
	@echo "Compiling target..."
	$(CLANG) -fpass-plugin=$(LLVM_PASS_LIB) -c $<
	$(CC) $(TARGET_OBJ) -L$(BUILD_DIR) -l$(RTLIB_LIB_NAME) -o $(TARGET)
	$(RM_F) $(TARGET_OBJ)

run: $(BUILD_DIR) $(TARGET) $(RTLIB_LIB_FILE)
	@echo "Running target..."
	export LD_LIBRARY_PATH=$(PWD)/$(BUILD_DIR):$LD_LIBRARY_PATH
	./$(TARGET)

$(BUILD_DIR):
	$(MKDIR_SAFE) $(BUILD_DIR)

clean:
	$(RM_RF) $(BUILD_DIR)
	$(RM_F) $(TARGET)
