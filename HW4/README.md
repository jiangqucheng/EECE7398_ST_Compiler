# Homework 4: Dominance

## Introduction

### Understanding Dominance Analysis in Control Flow Graphs

Dominance analysis is a fundamental concept in compiler optimization, crucial for understanding the structure of control flow within programs. It involves identifying dominance relationships among blocks in a Control Flow Graph (CFG), where a program is broken down into basic blocks connected by directed edges representing the possible flow of execution. This analysis is often used for advanced compiler optimizations like code motion, dead code elimination, and Static Single Assignment (SSA) form conversion.

This blog post delves into the key concepts of dominance analysis, including dominators, immediate dominators, and dominance frontiers. These concepts form the basis of various control flow optimizations and transformations.

### Key Concepts

#### Dominators
In a CFG, a block `BB1` is said to dominate another block `BB2` if every path from the entry block to `BB2` must pass through `BB1` . The entry block itself trivially dominates all other blocks in the graph because all execution paths must originate from it.

The concept of dominators can be useful to identify regions in the program where specific code fragments will always execute before others. This information is essential for optimizations such as moving invariant computations out of loops and removing unreachable code.

#### Immediate Dominators
Among the set of blocks that dominate a particular block, the one closest to in terms of control flow is known as its *immediate dominator*. The immediate dominator is unique for each block (except the entry block) and forms the basis of the *dominator tree*, a hierarchical structure that reveals the dominance relationships within the CFG.

In the dominator tree, each node represents a basic block, and an edge from `BB1` to `BB2` indicates that `BB1` is the immediate dominator of `BB2` . This tree structure helps in visualizing the control dependencies in a program.

#### Dominance Frontier
The *dominance frontier* of a block `BB1` is the set of all blocks where the dominance relationship breaks. More formally, a block `BBX` is in the dominance frontier of `BB1` if `BB1` dominates a predecessor of `BBX` , but `BB1` does not strictly dominate `BBX` itself.

Dominance frontiers are used to identify the points in the CFG where variables need to be merged or "phi-inserted" during SSA form conversion. This is important because it ensures that all possible values of a variable reaching a certain block are correctly accounted for.

### Control Flow Graph and Dominance Analysis

In the context of compiler design, the CFG represents the program's execution paths, with nodes corresponding to basic blocks and edges denoting control flow between them. Dominance analysis provides a way to understand the flow of control within a program by identifying how execution paths interact and where they converge or diverge.

#### The Role of Dominators in CFG
Dominators can be seen as checkpoints that ensure certain computations always happen before others. For example, if a block `BB1` dominates `BB2` , we can be certain that the execution of `BB2` implies the execution of `BB1` at some point. This property allows for optimizations such as moving loop-invariant computations out of loops, as the computations are guaranteed to occur before each iteration of the loop.

#### The Dominator Tree
The dominator tree provides a structured way to represent the dominance relationships within the CFG. By identifying the immediate dominator for each block, we can construct a tree where each block is a child of its immediate dominator. This structure is useful for identifying regions of code that are tightly coupled in terms of control flow, aiding in optimizations such as code motion and dead code elimination.

#### Understanding the Dominance Frontier
The dominance frontier is particularly useful in scenarios where multiple control paths converge. It helps identify the blocks where different execution paths must be reconciled, especially in the context of SSA form, where variables may have different values depending on the path taken to reach a block. By inserting "phi functions" at the dominance frontier, the compiler can correctly handle the merging of variable values from different paths.



## Detail Design

### Abstraction Classes

The abstraction class remain the same structure as last homework submittion, see detail in [HW3 - Abstraction Classes](https://github.com/jiangqucheng/EECE7398_ST_Compiler/tree/main/HW3#abstraction-classes).

I add one additional feature: `__lt__()` for class `BrilInstruction_Label`, therefore use current [`./bril_model`](https://github.com/jiangqucheng/EECE7398_ST_Compiler/tree/main/HW4/bril_model) for further development. 


### Dominance Analysis Implementation


The script `dom_analysis.py` is designed to perform dominance analysis on Bril program. It includes functionalities for generating a Control Flow Graph (CFG), computing dominators for each block, constructing the dominator tree, and identifying the dominance frontier. Below is a breakdown of the key parts of the code with brief notes on their functions and corresponding source code line indxx.

#### 1. **Imports and Argument Parsing**
   - The code imports necessary libraries like `os`, `networkx`, `pyvis`, and `matplotlib` for graph visualization, as well as custom modules from `bril_model`.
   - It also sets up argument parsing to allow the user to specify the Bril file to analyze and an optional save directory for generated outputs.
   https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/16fcb6796f098b2512a380d5c717b4d431890cbf/HW4/dom_analysis.py#L1-L46

#### 2. **Basic Block Definition**
   - This section defines the `BasicBlock` class, representing a basic block in the CFG. Each basic block consists of a label and a list of instructions.
   - It also includes properties for successors (`succ`) and predecessors (`pred`), which form the edges in the CFG.
   - The class implements various methods for equality checks, hashing, and string representation.
   https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/16fcb6796f098b2512a380d5c717b4d431890cbf/HW4/dom_analysis.py#L48-L86

#### 3. **Forming Basic Blocks from Bril Functions**
   - The function `iter_func_blocks` generates basic blocks from the provided Bril script by iterating over each function in the script and forming blocks based on instruction labels.
   - For functions without explicit labels, it creates anonymous basic blocks.
   https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/16fcb6796f098b2512a380d5c717b4d431890cbf/HW4/dom_analysis.py#L89-L101

#### 4. **Generating the CFG**
   - The `generate_func_cfg_dict` function builds the CFG by establishing the control flow between basic blocks. It adds `entry` and `return` blocks to represent the start and end points of a function.
   - It iterates over the blocks and updates the predecessors and successors based on control flow instructions (`jmp`, `br`, `ret`).
   https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/16fcb6796f098b2512a380d5c717b4d431890cbf/HW4/dom_analysis.py#L103-L156

#### 5. **Computing Dominators**
   - The `generate_dom_dict` function calculates the dominators for each block using an iterative fixed-point algorithm.
   - Initially, every block is assumed to dominate itself and all others. The algorithm repeatedly refines the dominator sets by intersecting the dominator sets of each block's predecessors.
   https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/16fcb6796f098b2512a380d5c717b4d431890cbf/HW4/dom_analysis.py#L162-L183

#### 6. **Immediate Dominator Calculation**
   - The `get_lease_superset_dom` function identifies the immediate dominator for a given block by finding the closest dominator in the dominator set.
   https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/16fcb6796f098b2512a380d5c717b4d431890cbf/HW4/dom_analysis.py#L185-L187

#### 7. **Dominance Frontier Computation**
   - The `get_dom_frontier` function determines the dominance frontier for a given block. It checks blocks where the dominance relationship changes based on control flow.
   https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/16fcb6796f098b2512a380d5c717b4d431890cbf/HW4/dom_analysis.py#L189-L191

#### 8. **Graph Visualization**
   - The code includes helper functions for generating graph visualizations using `Graphviz`. The functions `create_graphviz_dot_node` and `create_graphviz_dot_edge` create nodes and edges for the CFG and dominator tree graphs.
   - The `create_graphviz_dot` function produces separate visualizations for the CFG and dominator tree.
   https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/16fcb6796f098b2512a380d5c717b4d431890cbf/HW4/dom_analysis.py#L211-L258

#### 9. **Main Execution**
   - The script loads the specified Bril file and constructs the CFG for the functions in the script.
   - It then generates the dot files for the CFG and dominator tree, saving them in the specified directory.
   https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/16fcb6796f098b2512a380d5c717b4d431890cbf/HW4/dom_analysis.py#L261-L281

### Integration and Testing

The integration and testing phase focuses on verifying the correctness of the dominance analysis by evaluating its results against various test cases. The goal is to ensure that the dominance rules defined in the dominator tree are upheld for different basic block execution paths. This involves checking if any execution sequence violates the dominance relationships established by the analysis. To achieve this, the following steps are used:

1. **General Testing Approach**:
   - The basic and general idea of verification is to __iterate over all possible paths of execution__ in the Control Flow Graph (CFG) and validate the dominance properties. Specifically, we ensure that if block `BB1` dominates block `BB2`, then any execution path reaching `BB2` must pass through `BB1`.
   - For each basic block, we confirm that its set of dominators conforms to the expectations as derived from the dominator tree.
   - The results are compared against reference outputs from well-understood examples discussed in class, as well as other edge cases designed to stress test the analysis.
   - All analysis output are checked manually, and stored as the __golden snapshot using `turnt` toolchain__. To test any modification, use command `make turnt` to submit a fast check if anything have changed. 

2. **Test Cases**:
   - To thoroughly validate the implementation, several test cases in `.bril` format are used, which cover a variety of CFG structures. These include:
     - **Branching and Merging**: Simple branches where different paths converge into a single block. This tests if the dominance frontier is correctly identified.
     - **Loop Structures**:
       - **Natural Loops**: A basic loop where the execution repeatedly returns to the entry point. This checks if the analysis can handle back edges correctly.
       - **Cross Loops**: Where multiple loops share a common point, testing the algorithm's handling of intertwined control flows.
       - **Self-Loops**: Where a block jumps to itself, testing the edge case of dominance with cyclic behavior.
     - **Complex Branches**: Multi-level branching scenarios that test cascading decision-making processes.
     - **Select Cases with Fallthrough**: A switch-like structure where control can fall through to subsequent cases, testing non-trivial flow paths.
     - **Cycle with/without Header**: Examining cases where cycles may or may not have a designated entry block, testing the analysis of entry points and loop headers.
     - **Multiple Entry Points**: CFGs with more than one entry point, challenging the assumptions about where execution begins.

3. **Testing Execution**:
   - Each test case is analyzed using the implemented dominance utilities, and the results are compared against expected outputs derived manually or from reference solutions provided in class.
   - The verification process involves:
     1. **Dominators Check**: Ensuring that for each block `BB1`, its dominator set only contains blocks that dominate `BB1` as per the expected results.
     2. **Immediate Dominators Check**: Validating the immediate dominator for each block against the reference dominator tree structure.
     3. **Dominance Frontier Check**: Confirming that the dominance frontier of each block matches the expected set of blocks where the dominance relationship changes.

### Results and Analysis

👉 Check [HERE](https://github.com/jiangqucheng/EECE7398_ST_Compiler/tree/main/HW4/output) to see all graphical testcase results. 

The analysis results demonstrate the correctness and robustness of the dominance utilities. The generated dominance information (dominator sets, dominator tree, and dominance frontier) matches the expected results for all test cases. Below is a summary of the findings:

1. **Branching and Merging**:
   - The dominance analysis correctly identifies the blocks that dominate each branch and accurately determines the dominance frontiers where paths converge.
   ![image](https://github.com/user-attachments/assets/6270afdc-97ba-4535-beb3-f80045efeee9)
   https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/73249ed58947f2faad216637a8d2c3cac0a9af08/HW4/example/in_class_example_dom/Natural-Loops.golden-log#L1-L40

2. **Loop Structures**:
   - **Natural Loops**: The algorithm successfully handles back edges and identifies the loop entry points as dominators for the loop body.
   - **Cross Loops and Multiple Entry Points**: The implementation accurately distinguishes between blocks that dominate each shared section, even when the control flow is complex.
   - **Self-Loops**: Dominance analysis treats the block as dominating itself, which is correctly identified in the results.
   ![image](https://github.com/user-attachments/assets/cc748125-3301-455a-a2d0-d805e2408388)
   https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/73249ed58947f2faad216637a8d2c3cac0a9af08/HW4/example/in_class_example_dom/Cycle-with-Header-One-Entry-Point.golden-log#L1-L36
   https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/73249ed58947f2faad216637a8d2c3cac0a9af08/HW4/example/in_class_example_dom/Cycle-without-Header-Two-Entry-Points.golden-log#L1-L28

3. **Complex Branches and Fallthrough Cases**:
   - For cases with multiple branches and fallthrough behavior, the dominance frontier calculation correctly identifies the regions where the execution paths merge.
   - This indicates that the implementation can handle cases where control flow does not follow a simple pattern, such as switch statements with fallthrough.
   ![image](https://github.com/user-attachments/assets/bedd4433-5123-451f-b9f7-fb6328e156bd)
   https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/73249ed58947f2faad216637a8d2c3cac0a9af08/HW4/example/in_class_example_dom/Branch-Another-Example.golden-log#L1-L32
   https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/73249ed58947f2faad216637a8d2c3cac0a9af08/HW4/example/in_class_example_dom/Branch-Complex-Example.golden-log#L1-L48

4. **Other Edge Cases**:
   - Tests involving cycles without a clear header, and cases with two or more entry points, show that the analysis correctly computes dominators based on the actual paths from any entry to each block.
   - The results reveal that the dominance utilities can generalize beyond typical loop constructs, making them suitable for analyzing diverse control flow patterns.

5. **Other Real Benchmarks**:
   ![image](https://github.com/user-attachments/assets/dd81d68e-9451-4268-be0b-5b73d7edcb92)
   https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/73249ed58947f2faad216637a8d2c3cac0a9af08/HW4/example/in_class_example_df/in_class_example_1.golden-log#L1-L84
   Check [HERE](https://github.com/jiangqucheng/EECE7398_ST_Compiler/tree/main/HW4/output) to see all graphical test case results. 

## Conclusion

Dominance analysis is a key part of CFG-based optimizations in compilers. It involves:
- Identifying dominators to understand the flow of control.
- Using the immediate dominator to build the dominator tree.
- Computing the dominance frontier to manage variable merging.

These concepts enable powerful optimizations and transformations that improve program efficiency and correctness. In the following sections, we will explore how to implement dominance analysis in a compiler framework, test the correctness of the results, and apply these concepts to optimize real programs.

The integration and testing of the dominance analysis show that the implementation is reliable and performs well across a range of control flow scenarios. By comparing the analysis results with known references and carefully designed test cases, we ensure the correctness of the dominator tree construction and dominance frontier calculations.

The next steps involve using this verified dominance analysis for further compiler optimizations, such as SSA form conversion, dead code elimination, and loop-invariant code motion, leveraging the dominance relationships identified in this phase.
