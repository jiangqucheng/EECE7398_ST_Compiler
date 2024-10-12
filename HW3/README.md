# Homework 3: Data Flow

## Introduction

This assignment focuses on implementing dataflow analysis for the Bril intermediate language to support three major analyses: liveness, availability, and busy expressions. These analyses play a crucial role in various compiler optimizations, including Trivial Dead Code Elimination (DCE) and Local Value Numbering (LVN) that we discussed and implemented in previous homework, [HW2](https://github.com/jiangqucheng/EECE7398_ST_Compiler/tree/main/HW2). The goal is to analyze the flow of data within a program, identify redundant or unnecessary computations, and determine which values are still "live" or "in use" at various points in a program.

The report details the design of a flexible framework for these analyses, the implementation strategy for each type of dataflow analysis, and the use of visualization to display the results. The integration and testing process ensures the framework's correctness through various benchmark tests, and the results are analyzed to demonstrate its effectiveness.


## Detail Design

### Abstraction Classes

The abstraction class remain the same structure as last homework submittion, see detail in [HW2 - Abstraction Classes](https://github.com/jiangqucheng/EECE7398_ST_Compiler/tree/main/HW2#abstraction-classes).

I add some additional features and fix something like `__repr__` for some of the classes, therefore use current [`./bril_model`](https://github.com/jiangqucheng/EECE7398_ST_Compiler/tree/main/HW3/bril_model) for further development. 


### Graph Result Demonstration

Since this task is about analizing some properties of the data-flow graph, a better way to demonstrate it clear and straight forward is to show the computated result in visual format. I developed the framework to view analyze results using `vis.js` and `networkx`.

<!-- TODO: Video here -->
![2024-10-12 05-11-13](https://github.com/user-attachments/assets/754c3777-9e50-48cf-b29f-e96ad15e8e4e)
https://github.com/user-attachments/assets/29e63cef-2dde-4504-8d43-5998d673ca02




### Dataflow Analysis Implementation

The script `` performs dataflow analysis on Bril programs, supporting three types of analysis: `liveness`, `availability`, and `busy` expressions. The implementation is designed to be __generic__, allowing for easy extension to other types of dataflow analysis with minimal code changes.

---

#### 1. Argument Parsing and Setup

The script begins by utilizing the `argparse` module to handle command-line argument parsing. This allows the user to specify three key arguments when running the script:

- `ANALYSIS`: Specifies the type of dataflow analysis to perform. The valid options are `'liveness'`, `'availability'`, or `'busy'`. This argument is required and ensures the script knows what kind of analysis to perform on the Bril program.
- `DEMO_BRIL_FILE`: This is the path to the Bril program that will be analyzed. The file contains the intermediate representation (IR) of the program.
- `--save-dir`: An optional argument that specifies where to save the generated output HTML files (visualizations). If not provided, the default directory `./save` is used.

By parsing these arguments, the script can dynamically handle different types of analysis and ensure the correct files are processed and results saved to the right locations.

https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/601e0e9ae2116bd59ef11847346e94e5bc639a0f/HW3/df_analysis.py#L20-L25

---

#### 2. Validation of Arguments

Once the arguments are parsed, the script proceeds to validate them:

- `ANALYSIS`: The provided value is converted to lowercase for consistency. The script checks whether the specified analysis type is one of the allowed options: `'liveness'`, `'availability'`, or `'busy'`. If the user specifies an unsupported analysis, the script prints an error message and exits.
- `DEMO_BRIL_FILE`: The script checks if the provided file path exists on the system. If not, an error message is displayed, and the script terminates.
- If all validations pass, the script proceeds with the execution; otherwise, it prints the usage information (`parser.print_help()`) to guide the user on how to run the script correctly.

This ensures that only valid input and analysis types are processed.

https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/601e0e9ae2116bd59ef11847346e94e5bc639a0f/HW3/df_analysis.py#L27-L43

---

#### 3. Loading the Bril Script

The script loads the Bril program into a `BrilScript` object, which represents the structure of the input program. This object provides an abstraction over the Bril instructions and functions, making it easier to manipulate and analyze.

- The `BrilScript` object is initialized with the name of the file, and the control flow graph (CFG) for each function in the Bril script is constructed. The CFG represents how control flows between basic blocks (sequences of instructions without branches) in each function, which is crucial for performing dataflow analysis.
- `app_graph` is a dictionary that maps each `BrilFunction` to a tuple consisting of a `networkx` directed graph (the CFG) and a mapping of labels to their corresponding instructions.

The CFG provides the foundation for performing various types of dataflow analysis, as it organizes the program's structure into a form that can be traversed and analyzed.

https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/601e0e9ae2116bd59ef11847346e94e5bc639a0f/HW3/df_analysis.py#L135-L137

---

#### 4. Generating `GEN`, `KILL`, and `EXPR` Sets

For each basic block, the script calculates three sets:

- **`GEN`**: The set of variables used before being assigned a new value in the block. These are the variables that "generate" dependencies in the block.
- **`KILL`**: The set of variables that are redefined or "killed" within the block.
- **`EXPR`**: The set of expressions that are still available at the end of the block.

The function `get__args_used_before_assign__assigned__calc_expr_available_at_bb_end` iterates over the instructions in a basic block. It collects the following information:
- `used_first`: Variables that are used before any assignment in the block.
- `written`: Variables that are assigned new values within the block.
- `avail_exprs`: Expressions that remain available for future use at the end of the block, ensuring that they haven't been invalidated by any assignments.

The `GEN`, `KILL`, and `EXPR` sets are essential for performing dataflow analysis like liveness and availability, which rely on tracking how variables and expressions evolve over the program.

https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/601e0e9ae2116bd59ef11847346e94e5bc639a0f/HW3/df_analysis.py#L150-L168

---

#### 5. Updating `GEN`, `KILL`, and `EXPR` Sets

After calculating the `GEN`, `KILL`, and `EXPR` sets for each basic block, the script updates the CFG with this information. The `update_gen_kill_sets` function iterates over each node (basic block) in the CFG and stores the calculated `GEN`, `KILL`, and `EXPR` sets in the node's attributes.

This step enriches the CFG with the necessary dataflow information, setting up the foundation for more complex analyses like determining which variables are live or which expressions are available.

https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/601e0e9ae2116bd59ef11847346e94e5bc639a0f/HW3/df_analysis.py#L173-L180

---

#### 6. Generic Dataflow Analysis

The script defines a generic dataflow analysis function `_fdg_update_bare_bone`, which can be adapted for different types of analyses (liveness, availability, busy expressions). This function operates by traversing the CFG and updating the `IN` and `OUT` sets of each node (basic block):

- **`IN`**: The set of variables or expressions that are live or available at the entry to a basic block.
- **`OUT`**: The set of variables or expressions that are live or available at the exit of a basic block.

The function takes as input a specific analysis function (e.g., for liveness or availability) and applies it to update the `IN` and `OUT` sets for each node. The function also checks whether the `IN` and `OUT` sets change during the analysis—if they do, it indicates that the dataflow information has propagated, and further iterations are required.

The generic nature of this function minimizes code duplication and allows the script to easily switch between different types of analyses.

https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/601e0e9ae2116bd59ef11847346e94e5bc639a0f/HW3/df_analysis.py#L202-L213

---

#### 7. Specific Analysis Functions

The script defines specific analysis functions for each type of dataflow analysis:

- **Liveness Analysis**: Computes the `IN` and `OUT` sets based on the liveness of variables. It updates the sets by looking at the successors of each node and determining which variables are still live at the entry of a basic block.
  
- **Availability Analysis**: Determines which expressions are available at the entry and exit of a block. It considers the predecessor nodes and checks whether the expressions remain valid by avoiding any variables that were killed in the block.

- **Busy Expressions Analysis**: Identifies which expressions must be computed before reaching the next use of a variable. This analysis is useful for identifying common subexpressions that can be optimized.

Each function is passed to the generic `_fdg_update_bare_bone` function to perform the corresponding analysis.

https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/601e0e9ae2116bd59ef11847346e94e5bc639a0f/HW3/df_analysis.py#L215-L258

---

#### 8. Running the Analysis

The `update_analysis_sets` function orchestrates the execution of the selected analysis. Based on the user’s input (liveness, availability, or busy), the corresponding analysis function is retrieved from a mapping (`ANALYSIS_FUNC`). 

The analysis is executed iteratively, updating the CFG with the calculated `IN` and `OUT` sets until no further changes occur. This iterative approach is necessary because dataflow analysis typically involves propagating information through the CFG until a fixed point is reached (i.e., the point where further iterations don’t change the dataflow sets).

https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/601e0e9ae2116bd59ef11847346e94e5bc639a0f/HW3/df_analysis.py#L266-L277

---

#### 9. Visualization

The script concludes by generating a visual representation of the CFG using the `pyvis` library. It creates an interactive HTML file that displays the CFG along with the computed `IN`, `OUT`, `GEN`, `KILL`, and `EXPR` sets for each basic block.

- The `dump_into_pv_graph` function takes the CFG as input and converts it into a visual format. For each node (basic block) in the CFG, the `IN`, `OUT`, `GEN`, `KILL`, and `EXPR` sets are formatted as strings and added as attributes to the node in the visualization.
- The visualization allows users to interact with the CFG, inspect the dataflow information for each node, and understand the results of the analysis in a more intuitive manner.

This final step provides a clear and accessible way to verify the results of the analysis.

https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/601e0e9ae2116bd59ef11847346e94e5bc639a0f/HW3/df_analysis.py#L318-L376

---

### Conclusion

The script of `df_analysis.py` provides a flexible and extensible framework for performing dataflow analysis on Bril programs. By defining generic functions and specific analysis functions, it minimizes code duplication and allows for easy addition of new analysis types. The visualization step helps in understanding the results of the analysis by generating an interactive HTML representation of the CFG.


## Integration and Testing

The integration of the optimizations was done manually and thoroughly tested to ensure correctness. Testing was carried out using both class examples and official test cases from the Bril repository.

__Manual Testing__: To validate the correctness of the dataflow analysis, I manually executed the script on several examples provided during class lectures. This helped confirm that the basic dataflow functionality (liveness, availability, and busy expression analysis) was functioning as expected. To test each step of the workflow, use the `playground.ipynb` to break between steps and check output of each cell.

__Class Examples__: I tested the implementation with `in-class` examples, which serve as benchmarks for the expected output of liveness and availability analysis. Each example was carefully compared with the correct CFG and dataflow analysis results.

__Bril Benchmark Tests__: Additionally, I tested the system on Bril's official dataflow test cases found in `bril/examples/test/df/*.bril`. These benchmark examples cover edge cases and typical control flow scenarios, further ensuring the robustness of the implementation.

__Other Benchmarks__: Beyond the standard tests, I applied the analysis to select benchmarks from `bril/benchmarks/core`. These more complex scenarios helped confirm that the system could scale effectively while maintaining correct results.

Across all test cases, the output CFGs and the results of liveness, availability, and busy expressions analysis were consistent with the expected behavior. No discrepancies were found during manual inspection or benchmark comparisons.

BTW, to rerun all results that I submitted to this repo, just simply use `make`. 

## Results and Analysis

To make life easier, the Bril scripts that are tested in this HW are copied/created in the `./example` folder. The three types of dataflow analyses (`liveness`, `availability`, `busy`) were tested on the following :

- [`birthday.bril`](./example/birthday.bril)
- [`check-primes.bril`](./example/check-primes.bril)
- [`cond-args.bril`](./example/cond-args.bril)
- [`cond.bril`](./example/cond.bril)
- [`fact.bril`](./example/fact.bril)
- [`in_class_example_1.bril`](./example/in_class_example_1.bril)
- [`in_class_example_2.bril`](./example/in_class_example_2.bril)
- [`in_class_example_3.bril`](./example/in_class_example_3.bril)
- [`is-decreasing.bril`](./example/is-decreasing.bril)

To view the graph, set up a `http` server and use any of your favourite modern web browsers to open the `.html` file that just generated.

Example:
```bash 
❯ cd HW3
❯ python -m http.server
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
# Goto http://<server-ip>:8000/output/in_class_example_1.bril/liveness/in_class_example_1.html
```

### Liveness Analysis
Liveness analysis was correctly computed in all test cases. The variables that were "live" at each point in the program were accurately tracked. The results were particularly effective in identifying opportunities for Trivial DCE. For instance, variables that were defined but never live in subsequent instructions were correctly flagged, highlighting code that could be safely eliminated.

### Availability Analysis
Availability analysis was applied successfully, and all expressions available at the entry and exit of each basic block were correctly computed. This analysis is critical for Local Value Numbering (LVN), where equivalent expressions are consolidated. In benchmarks such as in_class_example_3.bril, the implementation showed how redundant computations could be eliminated by detecting available expressions early.

### Busy Expressions Analysis
Busy expressions analysis worked as expected, identifying expressions that were critical to compute before the next use. This was particularly useful in loops, where understanding which expressions are "busy" helps optimize the repeated evaluation of the same values.

### Comparison and Insights
For all test cases, I carefully compared the output CFG and dataflow graph to the expected results. No differences were found in any of the test cases, confirming that the implementation is consistent with the theoretical expectations for dataflow analysis.

The visual representation of the analysis results (generated using vis.js and networkx) provided an intuitive way to verify the correctness of the `IN`, `OUT`, `GEN`, `KILL`, and `EXPR` sets for each basic block. This helped to easily identify points of optimization and confirmed that the framework was operating as intended.


### Raw test log

Check the following pages: 
<!-- TODO: add the markdown iframe to graph.html -->


## Conclusion

The dataflow analysis framework for Bril successfully implements liveness, availability, and busy expressions analyses, all of which are foundational for key compiler optimizations. Trivial Dead Code Elimination (DCE) and Local Value Numbering (LVN) will extremely benefit from these analyses by eliminating redundant computations and identifying unused variables.

The testing of the framework on various Bril programs—ranging from simple in-class examples to more complex benchmark scripts—demonstrates that the analyses work correctly and efficiently. The interactive visualizations of the control flow graph (CFG) and associated dataflow sets provide valuable insights, making it easier to verify correctness and identify optimization opportunities.

This project establishes a strong foundation for performing local optimizations on intermediate representations like Bril. Future work could extend the framework to handle interprocedural analyses, multi-block optimizations, or more advanced global dataflow analyses. By further refining these optimizations, we can significantly enhance the efficiency of compiled programs.

