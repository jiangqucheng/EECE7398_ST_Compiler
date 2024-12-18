# Homework 5: LLVM: Spinning Up

## Env 

### Env setup

New dependency packages are required to build targets in this Homework. I choose using `conda` for clear isolation with the system build toolchain. However, things were much more difficult than ever if the idiot VSCode (and unreliable official plugins) came to the context: VSCode IntelliSense could not easily recognize the header file, although LSP had already found out where to go; copilot continued to ask me to fix the include path to clear these import error; and the corresponding items in setting panel I have specified and pointed to the correct direction is always ignored or overwritten by their default location, which is point to the system default path. After trying a bunch of suggestions posted in the VSCode community forum, I finally gave up on making the autocomplete and type-checking stuff work. 

```bash
conda install conda-forge::clang
conda install conda-forge::cmake
conda install -c conda-forge llvmdev;  # header file, cmake recipe
```

After experiencing these kinds of frustrating config stuff, I strongly recommend installing/updating the system's default LLVM toolchain to make VSCode find the definition of the functions and variables, and not draw red underlines to interrupt your mind. 

### Env startup

If the LLVM toolchain is installed in the system-level default location, there's no need to do this extra step. 

```bash
export LLVM_DIR=$CONDA_PREFIX/lib/cmake/llvm
export LD_LIBRARY_PATH=<PRJ_DIR>/HW5/llvm-passes/show-float-div/build:$LD_LIBRARY_PATH;
```

## Detail Design

There're __3__ passes implemented in this Homework: 
- __loop-unroll__: Implemented a straightforward loop unrolling pass, only unrolling once if it finds a valid loop. (An ambitious task as the instruction of this homework suggested.)
- __show-bin-op__: Display when there is a binary operation, log it out when doing compile, and call a stab function in `rtlib` during runtime to print the value stored in the destination. 
- __show-float-div__: As the instruction of this homework suggested, this pass is an example of an unambitious task, which displays only the `fdiv` operation, and acts the very same as the `show-bin-op` pass does when encountering `fdiv` operation.

_* Check [Passes Source Code](https://github.com/jiangqucheng/EECE7398_ST_Compiler/tree/main/HW5/llvm-passes) for details._

## Integration, Testing

Some examples of the _real-ish_ C/C++ program are provided in this homework.
- `example.c` in each pass: Unit Tests to make sure passes are performing the correct results as wished. 
- `matmul.cpp`: A square matrix multiply testbench, which would be a great scenario to test the loop unrolling pass, but also can test the other two display passes. 
- `projectile_motion.cpp`: Simulates the motion of a projectile launched at a given angle and initial velocity within finite N steps.

To build the tests:

For `examples.c` and the pass library, go to each pass folder, and run `make`. All the results will be generated, including: 
- `$(BUILD_DIR)/$(PASS_NAME)/$(PASS_NAME)Pass.so`: Pass plugin as a dynamic lib.
- `$(BUILD_DIR)/lib$(RTLIB_LIB_NAME).so`: Additional Runtime functions (i.e. Stab call funcs).
- `example`: Executable of `examples.c`.
To run the `example`, use `make run` instead of `make`. 

For `matmul.cpp` and `projectile_motion.cpp`, go to the app folder, and run `make`. Executable will be generated in the same folder.
Use `make run` to test the execution.

## Results and Analysis

### Matrix Multiply - Loop Unroll

Slightly different in wall clock speed.
```bash
❯ make run
Running target with custom LLVM pass...
time ./matmul_with_pass
C[0][0] = 200
0.02user 0.00system 0:00.02elapsed 96%CPU (0avgtext+0avgdata 2772maxresident)k
0inputs+0outputs (0major+149minor)pagefaults 0swaps
Running target without custom LLVM pass...
time ./matmul_without_pass
C[0][0] = 200
0.01user 0.00system 0:00.02elapsed 95%CPU (0avgtext+0avgdata 2896maxresident)k
0inputs+0outputs (0major+153minor)pagefaults 0swaps
```


### Example - Show `FDiv`

```bash
# ~/scratch/work/course/EECE7398_ST_Compiler/HW5/llvm-passes/show-float-div    main !8 ?7      ✔  15s   course-eece7398-st-compiler   jiang@builder  04:29:01  

❯ make clean
❯ make run
mkdir -p build
Building RTLib...
make[1]: Entering directory '/scratch/work/course/EECE7398_ST_Compiler/HW5/llvm-passes/show-float-div'
make[1]: 'build' is up to date.
make[1]: Leaving directory '/scratch/work/course/EECE7398_ST_Compiler/HW5/llvm-passes/show-float-div'
clang -fPIC -shared rtlib.c -o build/librtlib.so
Building LLVM Pass...
make[1]: Entering directory '/scratch/work/course/EECE7398_ST_Compiler/HW5/llvm-passes/show-float-div'
make[1]: 'build' is up to date.
make[1]: Leaving directory '/scratch/work/course/EECE7398_ST_Compiler/HW5/llvm-passes/show-float-div'
cd build && cmake .. && make
-- The C compiler identification is GNU 14.2.0
-- The CXX compiler identification is GNU 9.4.0
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working C compiler: /home/jiang/miniconda3/envs/course-eece7398-st-compiler/bin/cc - skipped
-- Detecting C compile features
-- Detecting C compile features - done
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Check for working CXX compiler: /usr/bin/c++ - skipped
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Found ZLIB: /usr/lib/x86_64-linux-gnu/libz.so (found version "1.2.11")
-- Found zstd: /home/jiang/miniconda3/envs/course-eece7398-st-compiler/lib/libzstd.so
-- Found LibXml2: /home/jiang/miniconda3/envs/course-eece7398-st-compiler/lib/libxml2.so (found version "2.13.1")
-- Linker detection: GNU ld
-- Registering ShowFDivPass as a pass plugin (static build: OFF)
-- Configuring done (0.7s)
-- Generating done (0.0s)
-- Build files have been written to: /home/jiang/scratch/work/course/EECE7398_ST_Compiler/HW5/llvm-passes/show-float-div/build
make[1]: Entering directory '/scratch/work/course/EECE7398_ST_Compiler/HW5/llvm-passes/show-float-div/build'
make[2]: Entering directory '/scratch/work/course/EECE7398_ST_Compiler/HW5/llvm-passes/show-float-div/build'
make[3]: Entering directory '/scratch/work/course/EECE7398_ST_Compiler/HW5/llvm-passes/show-float-div/build'
make[3]: Leaving directory '/scratch/work/course/EECE7398_ST_Compiler/HW5/llvm-passes/show-float-div/build'
make[3]: Entering directory '/scratch/work/course/EECE7398_ST_Compiler/HW5/llvm-passes/show-float-div/build'
[ 50%] Building CXX object ShowFDiv/CMakeFiles/ShowFDivPass.dir/ShowFDiv.cpp.o
[100%] Linking CXX shared module ShowFDivPass.so
make[3]: Leaving directory '/scratch/work/course/EECE7398_ST_Compiler/HW5/llvm-passes/show-float-div/build'
[100%] Built target ShowFDivPass
make[2]: Leaving directory '/scratch/work/course/EECE7398_ST_Compiler/HW5/llvm-passes/show-float-div/build'
make[1]: Leaving directory '/scratch/work/course/EECE7398_ST_Compiler/HW5/llvm-passes/show-float-div/build'
Compiling target...
clang -fpass-plugin=build/ShowFDiv/ShowFDivPass.so -c example.c

ShowFDiv.cpp:34: Found FDiv operator:   %38 = fdiv double %37, 2.000000e+00
  %38 = fdiv double %37, 2.000000e+00
OpcodeName: fdiv

clang example.o -Lbuild -lrtlib -o example
rm -f example.o
Running target...
export LD_LIBRARY_PATH=/home/jiang/scratch/work/course/EECE7398_ST_Compiler/HW5/llvm-passes/show-float-div/build:$LD_LIBRARY_PATH && \
./example
Enter a number: 123
125
121
246
61
Enter a float number: 123.456
125.456001
121.456001
246.912003
[logfdiv: 61.728001 = 123.456001 / 2.000000]
61.728001
```

