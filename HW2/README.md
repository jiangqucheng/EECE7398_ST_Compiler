# Homework 2: Optimizing with DCE and LVN

## Introduction

This assignment aims to implement two key local optimizations for the Bril intermediate language: Trivial Dead Code Elimination (DCE) and Local Value Numbering (LVN). These optimizations enhance the efficiency of Bril programs by removing unnecessary instructions and consolidating equivalent expressions. This report outlines the development process, testing methodology, and analysis of the implemented optimizations.


## Detail Design

### Abstraction Classes

The core of the Bril language representation in this project is implemented in the `bril_model/_bril_struct.py` file. This module provides a structured and object-oriented way to represent Bril programs (`BrilScript`), functions (`BrilFunction`), and instructions (`BrilInstruction`). Each Bril instruction is modeled as a Python object, enabling intuitive manipulation and transformation of the program during optimization.

The primary classes include:

**Bril Program**: Represents the entire Bril program, containing multiple functions.

**Bril Function**: Encapsulates a sequence of instructions and metadata for a function within the program.

**Bril Instruction**: Models individual instructions, differentiating between operations (e.g., addition, multiplication) and effectful statements (e.g., print).

First, the `BrilInstruction` class is the base class for all instructions. Its constructor accepts a dictionary `raw` and deeply copies its contents into the instance variable `_raw`. It also initializes a mark dictionary `_marks` to track whether the instruction has been deleted, modified, or replaced. The constructor also checks whether the key in the raw dictionary is in the allowed key set `AVAILABLE_KEYS`, and throws `NotImplementedError` if there is an unrecognized key. The class also defines a series of properties and methods for accessing and modifying various parts of the instruction, such as `dest`, `type`, `op`, `args`, etc.

Next are several subclasses inherited from `BrilInstruction`, which handle different types of instructions. The `BrilInstruction_Const` class is used to handle constant instructions. It checks whether the opcode is const in the constructor and verifies whether the key in the dictionary is in the allowed set. The `BrilInstruction_Label` class is used to handle label instructions. It checks whether the label exists in the constructor and verifies the key in the dictionary. The `BrilInstruction_ValOp` class is used to handle operation instructions with a return value. It checks whether the opcode is in the allowed set and verifies the key in the dictionary in the constructor. The `BrilInstruction_EffOp` class is used to handle operation instructions without a return value. It performs similar checks and verifications in the constructor.

The `BrilFunction` class is used to represent a Bril function. Its constructor accepts a dictionary raw and extracts the instruction list `instrs` from it, converting each instruction into a corresponding `BrilInstruction` subclass instance. It also checks whether the key in the dictionary is in the allowed set. The class also defines some properties and methods for accessing and modifying various parts of the function, such as `name`, `type`, `args`, etc.

Finally, the `BrilScript` class is used to represent a Bril script. Its constructor accepts a dictionary `raw` and extracts the function list `functions` from it, converting each function into a `BrilFunction` instance. It also checks whether the key in the dictionary is in the allowed set. The class also defines some properties and methods for accessing and modifying various parts of the script, such as `functions`, etc.

Together, these classes form a framework for processing Bril language instructions and scripts, providing a wealth of properties and methods to access and modify various parts of instructions and scripts.



### Trivial Dead Code Elimination (DCE)

The Trivial-DCE implementation is encapsulated in `tdce.py`. This script scans through the instructions of a Bril function and removes any instructions whose results are not used before being overwritten. The optimization process involves:

The `trivial_dce_once` function performs a dead code elimination operation. It traverses all instructions in the function, collects all used variables, and marks unused instructions for deletion. Then, it updates the function's instruction list, deletes the instructions marked for deletion, and returns a Boolean value indicating whether the instruction is deleted.

The `trivial_dce` function is a loop that repeatedly calls the `trivial_dce_once` function until no more instructions are deleted.

The `_block_mark_reassign_before_use` function deletes instructions that are reassigned before use within a single basic block. It maintains a dictionary to track the most recent unused assignment instructions and deletes old assignment instructions before reassignment is found.

The `rm_reassign_before_use` function traverses all basic blocks of the function, calls the _block_mark_reassign_before_use function to delete instructions that are reassigned before use, and updates the function's instruction list.

The `trivial_dce_plus` function combines function-level dead code elimination with instruction removal before reassignment until there are no more instructions to remove.

This straightforward approach efficiently eliminates redundant calculations, contributing to a cleaner and faster program.


### Local Value Numbering (LVN)

Local Value Numbering optimization is implemented in `lvn.py`, LVN assigns unique numbers to distinct computations to detect and eliminate redundant expressions within a single block. Key steps include:

**Numbering Expressions**: LVN assigns a unique identifier to each distinct computation. This identifier, or value number, is used to track expressions within a block. If an identical computation is encountered later, the existing value number is reused, eliminating the need to recompute the expression.
For example, if the expression `a + b` is already computed and assigned a value number, any subsequent occurrence of `a + b` will directly use the same value number instead of recalculating the result.

**Simplification and Substitution**: The script replaces redundant operations with precomputed values or previously assigned variables, reducing the number of cpu-intense operations in the block. This is done by looking up the value number table for existing computations and substituting them wherever possible.
By minimizing redundant calculations, LVN not only optimizes runtime performance but also simplifies the code.

**Constant Folding**: Constant folding is a compile-time optimization technique that evaluates expressions with known constant values. For instance, an expression like `const 2 + const 3` is directly replaced with `const 5`. In the script, a dictionary named `FOLDABLE_OPS` maps operation names (e.g., `add`, `mul`, `sub`) to their respective lambda functions that perform the computation. When the LVN process encounters an expression with constant arguments, it applies the corresponding function to compute the result immediately. _Credit: [Bril Official Example](https://github.com/sampsyo/bril/blob/main/examples/lvn.py)_

**Expression Tracking and Reuse**: An `Expr` class is defined to uniquely represent computations in terms of operations and their arguments. This allows the LVN process to easily check if a computation has been previously performed and reuse the result if possible.
The implementation also handles commutative operations (e.g., `add`, `mul`, `and`, `or`, `eq`) by normalizing the order of arguments, ensuring that expressions like `a + b` and `b + a` are recognized as identical.


## Integration and Testing
The `brench` tool is used for batch testing both optimizations across a variety of Bril programs. The `brench_test_lvn.toml` and `brench_test_tdce.toml` configuration files specify the programs and expected results for LVN and DCE tests, respectively. This ensures that both optimizations work correctly and consistently.

As defined in `brench_test_lvn.toml`, we specifies the path to the Bril benchmark programs to be tested, which are all the `*.bril` located in the `../bril/benchmarks/core/`.

The configuration file defines multiple test run pipelines, each of which is defined in the `[runs.<name>]` section. Each pipeline contains a pipeline field that lists the sequence of commands to be executed.

The `baseline` pipeline is a baseline test without any optimization. It first converts the Bril program to JSON format and then runs the program using the brili interpreter.

The `hw2p1_s0` pipeline is used to test whether the input and output structures are correct, but it does not perform any optimization. The purpose of this pipeline is to test if the Bril Construction work has no bug in it. 

The `hw2p1_s1` pipeline tests simple dead code elimination optimization. It calls the `tdce.py` script and passes the `tdce` parameter to enable function-level dead code elimination.

The `hw2p1_s2` pipeline tests the instruction removal optimization used before revalue. It calls the `tdce.py` script and passes the `raby` argument to enable the `rm_reassign_before_use` pass optimization.

The `hw2p1_s3` pipeline combines function-level dead code elimination and instruction removal optimization used before revalue. It calls the `tdce.py` script and passes the `tdce+` argument to enable both optimizations.

Each pipeline ultimately runs the optimized Bril program using the `brili` interpreter, passing arguments via the `-p {args}` option.


## Results and Analysis

The optimizations were tested using `brench` tool, which verifies the correctness and performance of the implemented passes. The tool checks the `brili` Standard Output (`STDOUT`) for each test specification to ensure that the optimized programs produce the same results as their unoptimized counterparts. This rigorous testing confirms that the optimization passes do not alter the semantics of the Bril programs.

The testing demonstrated significant improvements in reducing the number of executed instructions for each Bril program. Programs with redundant calculations and unused instructions were simplified, leading to a reduced instruction count and faster execution times (based on Instructions Executed reported by `brili -p`). 

For example, in the original benchmark `check-primes`, the program required _8,468_ instructions to complete its execution. After applying the `hw2p1_s3` optimization pipeline (DCE-only), the number of instructions executed was reduced to _8,419_. Furthermore, using the `hw2p2_s2` optimization pipeline (LVN+DCE), the total instructions executed dropped significantly to _4,238_, representing a reduction to _50.05%_ of the original execution time. This demonstrates the substantial impact of combining LVN and DCE optimizations on program efficiency.

### Raw test log

```bash
❯ brench brench_test_tdce.toml
benchmark,run,result
fact,baseline,229
fact,hw2p1_s0,229
fact,hw2p1_s1,228
fact,hw2p1_s2,229
fact,hw2p1_s3,228
quadratic,baseline,785
quadratic,hw2p1_s0,785
quadratic,hw2p1_s1,783
quadratic,hw2p1_s2,785
quadratic,hw2p1_s3,783
recfact,baseline,104
recfact,hw2p1_s0,104
recfact,hw2p1_s1,103
recfact,hw2p1_s2,104
recfact,hw2p1_s3,103
pascals-row,baseline,146
pascals-row,hw2p1_s0,146
pascals-row,hw2p1_s1,139
pascals-row,hw2p1_s2,146
pascals-row,hw2p1_s3,139
loopfact,baseline,116
loopfact,hw2p1_s0,116
loopfact,hw2p1_s1,115
loopfact,hw2p1_s2,116
loopfact,hw2p1_s3,115
sum-sq-diff,baseline,3038
sum-sq-diff,hw2p1_s0,3038
sum-sq-diff,hw2p1_s1,3036
sum-sq-diff,hw2p1_s2,3038
sum-sq-diff,hw2p1_s3,3036
birthday,baseline,484
birthday,hw2p1_s0,484
birthday,hw2p1_s1,483
birthday,hw2p1_s2,484
birthday,hw2p1_s3,483
mod_inv,baseline,558
mod_inv,hw2p1_s0,558
mod_inv,hw2p1_s1,555
mod_inv,hw2p1_s2,558
mod_inv,hw2p1_s3,555
check-primes,baseline,8468
check-primes,hw2p1_s0,8468
check-primes,hw2p1_s1,8419
check-primes,hw2p1_s2,8468
check-primes,hw2p1_s3,8419
bitwise-ops,baseline,1690
bitwise-ops,hw2p1_s0,1690
bitwise-ops,hw2p1_s1,1689
bitwise-ops,hw2p1_s2,1690
bitwise-ops,hw2p1_s3,1689
relative-primes,baseline,1923
relative-primes,hw2p1_s0,1923
relative-primes,hw2p1_s1,1914
relative-primes,hw2p1_s2,1923
relative-primes,hw2p1_s3,1914
euclid,baseline,563
euclid,hw2p1_s0,563
euclid,hw2p1_s1,562
euclid,hw2p1_s2,563
euclid,hw2p1_s3,562
primes-between,baseline,574100
primes-between,hw2p1_s0,574100
primes-between,hw2p1_s1,574100
primes-between,hw2p1_s2,574100
primes-between,hw2p1_s3,574100
sum-check,baseline,5018
sum-check,hw2p1_s0,5018
sum-check,hw2p1_s1,5018
sum-check,hw2p1_s2,5018
sum-check,hw2p1_s3,5018
armstrong,baseline,133
armstrong,hw2p1_s0,133
armstrong,hw2p1_s1,130
armstrong,hw2p1_s2,133
armstrong,hw2p1_s3,130
```

```bash

❯ brench brench_test_lvn.toml
benchmark,run,result
fact,baseline,229
fact,hw2p2_s1,229
fact,hw2p2_s2,167
is-decreasing,baseline,127
is-decreasing,hw2p2_s1,127
is-decreasing,hw2p2_s2,123
quadratic,baseline,785
quadratic,hw2p2_s1,785
quadratic,hw2p2_s2,500
recfact,baseline,104
recfact,hw2p2_s1,104
recfact,hw2p2_s2,64
fizz-buzz,baseline,3652
fizz-buzz,hw2p2_s1,3652
fizz-buzz,hw2p2_s2,2103
pascals-row,baseline,146
pascals-row,hw2p2_s1,146
pascals-row,hw2p2_s2,68
loopfact,baseline,116
loopfact,hw2p2_s1,116
loopfact,hw2p2_s2,78
reverse,baseline,46
reverse,hw2p2_s1,46
reverse,hw2p2_s2,38
sum-sq-diff,baseline,3038
sum-sq-diff,hw2p2_s1,3038
sum-sq-diff,hw2p2_s2,1717
birthday,baseline,484
birthday,hw2p2_s1,484
birthday,hw2p2_s2,278
mod_inv,baseline,558
mod_inv,hw2p2_s1,558
mod_inv,hw2p2_s2,304
check-primes,baseline,8468
check-primes,hw2p2_s1,8468
check-primes,hw2p2_s2,4238
bitwise-ops,baseline,1690
bitwise-ops,hw2p2_s1,1690
bitwise-ops,hw2p2_s2,1689
relative-primes,baseline,1923
relative-primes,hw2p2_s1,1923
relative-primes,hw2p2_s2,1207
euclid,baseline,563
euclid,hw2p2_s1,563
euclid,hw2p2_s2,272
primes-between,baseline,574100
primes-between,hw2p2_s1,574100
primes-between,hw2p2_s2,571439
perfect,baseline,232
perfect,hw2p2_s1,232
perfect,hw2p2_s2,231
bitshift,baseline,167
bitshift,hw2p2_s1,167
bitshift,hw2p2_s2,104
sum-check,baseline,5018
sum-check,hw2p2_s1,5018
sum-check,hw2p2_s2,5018
armstrong,baseline,133
armstrong,hw2p2_s1,133
armstrong,hw2p2_s2,130
```



## Conclusion

The implementation successfully optimizes Bril programs through Trivial Dead Code Elimination and Local Value Numbering. Both techniques were integrated and tested using brench, confirming their effectiveness. Future work could focus on extending these optimizations to handle more complex cases, such as multi-block programs and interprocedural optimizations.

This project demonstrates the power of local optimizations in streamlining intermediate representations and serves as a solid foundation for further exploration of compiler optimization techniques.

