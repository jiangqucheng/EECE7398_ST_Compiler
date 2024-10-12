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


### Dataflow Analysis Implementation

The script `` performs dataflow analysis on Bril programs, supporting three types of analysis: `liveness`, `availability`, and `busy` expressions. The implementation is designed to be __generic__, allowing for easy extension to other types of dataflow analysis with minimal code changes.

#### 1. Argument Parsing and Setup

The script starts by parsing command-line arguments to determine the type of analysis to perform and the input Bril file.

```python
import argparse
parser = argparse.ArgumentParser(description='Generate data flow graph for a bril script')
parser.add_argument('ANALYSIS', type=str, help='Analysis: [liveness, availability, busy]')
parser.add_argument('DEMO_BRIL_FILE', type=str, help='Path to the bril file')
parser.add_argument('--save-dir', type=str, default='./save', help='Path to save the generated html files')
args = parser.parse_args()
```
_\*Reference: https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/601e0e9ae2116bd59ef11847346e94e5bc639a0f/HW3/df_analysis.py#L20-L25_

#### 2. Validation of Arguments

The script validates the provided arguments to ensure the analysis type is supported and the input file exists.

```python
ANALYSIS = args.ANALYSIS.lower()
DEMO_BRIL_FILE = args.DEMO_BRIL_FILE
SAVE_DIR = args.save_dir

correct = True
if ANALYSIS not in ['liveness', 'availability', 'busy']:
    print(f"Analysis <{ANALYSIS}> not supported")
    correct = False
if not os.path.exists(DEMO_BRIL_FILE):
    print(f"File <{DEMO_BRIL_FILE}> not found")
    correct = False
if not correct:
    parser.print_help()
    exit(1)
```
_\*Reference: https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/601e0e9ae2116bd59ef11847346e94e5bc639a0f/HW3/df_analysis.py#L27-L43_


#### 3. Loading the Bril Script

The Bril script is loaded into a `BrilScript` object, and the control flow graph (CFG) is constructed for each function.

```python
bbs = bm.BrilScript(script_name=os.path.basename(DEMO_BRIL_FILE), file_dir=os.path.dirname(DEMO_BRIL_FILE))
app_graph: Dict[bm.BrilFunction, Tuple[nx.DiGraph, Dict[bm.BrilInstruction_Label, List[bm.BrilInstruction]]]] = {}
update_to_graph(bbs, app_graph)
```
_\*Reference: https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/601e0e9ae2116bd59ef11847346e94e5bc639a0f/HW3/df_analysis.py#L135-L137_


#### 4. Generating GEN, KILL, and EXPR Sets

For each basic block, the script calculates the sets of variables and expressions that are used before being defined (GEN), modified (KILL), and available at the end of the block (EXPR).

```python
def get__args_used_before_assign__assigned__calc_expr_available_at_bb_end(instrs: List[bm.BrilInstruction]) -> Tuple[Set[str],Set[str],Set[Expr]]:
    used_first: Set[str] = set()
    written: Set[str] = set()
    avail_exprs: Set[Expr] = set()
    for instr in instrs:
        used_first.update(set(instr.args if instr.args else []) - written)
        if instr.dest:
            for expr in list(avail_exprs):
                if instr.dest in expr.args:
                    avail_exprs.remove(expr)
            written.add(instr.dest)
            if instr.args and instr.op not in ['id', 'const', 'call']:
                avail_exprs.add(Expr(instr.op, instr.args))
    return used_first, written, avail_exprs
```
_\*Reference: https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/601e0e9ae2116bd59ef11847346e94e5bc639a0f/HW3/df_analysis.py#L150-L168_


#### 5. Updating GEN, KILL, and EXPR Sets

The script updates the GEN, KILL, and EXPR sets for each basic block in the CFG.

```python
def update_gen_kill_sets(app_graph: Dict[bm.BrilFunction, Tuple[nx.DiGraph, Dict[bm.BrilInstruction_Label, List[bm.BrilInstruction]]]]):
    for _, (fdg, _) in app_graph.items():
        for each_node, each_node_data in fdg.nodes(data=True):
            each_block: List[bm.BrilInstruction] = each_node_data.get('instructions', None)
            _gen, _kill, _expr = gen_kill_expr_sets(each_block) if each_block else (set(), set(), set())
            fdg.nodes[each_node]['GEN'] = _gen
            fdg.nodes[each_node]['KILL'] = _kill
            fdg.nodes[each_node]['EXPR'] = _expr
```
_\*Reference: https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/601e0e9ae2116bd59ef11847346e94e5bc639a0f/HW3/df_analysis.py#L173-L180_


#### 6. Generic Dataflow Analysis

The script defines a generic function `_fdg_update_bare_bone` that performs the common part of the analysis. This function is then used to implement specific analysis types (liveness, availability, busy).

```python
def _fdg_update_bare_bone(specific_analysis_func: Callable[[nx.DiGraph, str], Tuple[Set[str], Set[str]]], fdg: nx.DiGraph) -> bool:
    has_changed = False
    for this_node, _ in fdg.nodes(data=True):
        _in, _out = specific_analysis_func(fdg, this_node)
        if _in != _get_node_in_set(fdg, this_node) or _out != _get_node_out_set(fdg, this_node):
            fdg.nodes[this_node]['IN'] = _in
            fdg.nodes[this_node]['OUT'] = _out
            has_changed = True
    return has_changed
```
_\*Reference: https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/601e0e9ae2116bd59ef11847346e94e5bc639a0f/HW3/df_analysis.py#L202-L213_


#### 7. Specific Analysis Functions

The script defines specific functions for each type of analysis, which are passed to the generic function.

```python
def _fdg_update_internal_liveness_sets(fdg: nx.DiGraph, this_node: str) -> Tuple[Set[str], Set[str]]:
    _temp_succ_req = [_get_node_in_set(fdg, each_succ_node) for each_succ_node in _get_node_succ_set(fdg, this_node)]
    _out: Set[str] = set.union(*_temp_succ_req) if _temp_succ_req else set()
    _in: Set[str] = set.union(_get_node_gen_set(fdg, this_node), set.difference(_out, _get_node_kill_set(fdg, this_node)))
    return _in, _out

def _fdg_update_internal_availability_sets(fdg: nx.DiGraph, this_node: str) -> Tuple[Set[Expr], Set[Expr]]:
    _temp_pred_give = [_get_node_out_set(fdg, each_pred_node) for each_pred_node in _get_node_pred_set(fdg, this_node)]
    _in: Set[Expr] = set.intersection(*_temp_pred_give) if _temp_pred_give else set()
    _out: Set[Expr] = set.union(_get_node_in_set(fdg, this_node), _get_node_expr_set(fdg, this_node))
    _out = set([each_expr for each_expr in _out if not set.intersection(set(each_expr.args), _get_node_kill_set(fdg, this_node))])
    return _in, _out

def _fdg_update_internal_busy_sets(fdg: nx.DiGraph, this_node: str) -> Tuple[Set[Expr], Set[Expr]]:
    _temp_succ_req = [_get_node_in_set(fdg, each_succ_node) for each_succ_node in _get_node_succ_set(fdg, this_node)]
    _out: Set[Expr] = set.intersection(*_temp_succ_req) if _temp_succ_req else set()
    _in: Set[Expr] = set([each_expr for each_expr in _out if not set.intersection(set(each_expr.args), _get_node_kill_set(fdg, this_node))])
    _in = set.union(_in, _get_node_expr_set(fdg, this_node))
    return _in, _out
```
_\*Reference: https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/601e0e9ae2116bd59ef11847346e94e5bc639a0f/HW3/df_analysis.py#L215-L258_


#### 8. Running the Analysis

The script runs the selected analysis type by calling the `update_analysis_sets` function.

```python
def update_analysis_sets(analysis_type_str: str , app_graph: Dict[bm.BrilFunction, Tuple[nx.DiGraph, Dict[bm.BrilInstruction_Label, List[bm.BrilInstruction]]]]):
    analysis_func = ANALYSIS_FUNC.get(analysis_type_str, None)
    if not analysis_func:
        print(f"Analysis <{analysis_type_str}> not supported")
        return
    has_changed = True
    while has_changed:
        has_changed = False
        for _, (fdg, _) in app_graph.items():
            has_changed |= _fdg_update_bare_bone(analysis_func, fdg)
```
_\*Reference: https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/601e0e9ae2116bd59ef11847346e94e5bc639a0f/HW3/df_analysis.py#L266-L277_


#### 9. Visualization

Finally, the script generates an HTML visualization of the CFG with the computed IN and OUT sets for each node.

```python
def dump_into_pv_graph(fdg: nx.DiGraph) -> pv.network.Network:
    net = pv.network.Network(
        directed=True,
        neighborhood_highlight=True,
        notebook=True,
        cdn_resources="jiang", 
        height="100vh",
        width="100vw",
    )
    net.from_nx(fdg)
    for node in net.nodes:
        node['IN'] = _in = generate_set_str(node.pop('IN', set()))
        node['OUT'] = _out = generate_set_str(node.pop('OUT', set()))
        node['GEN'] = _gen = generate_set_str(node.pop('GEN', set()))
        node['KILL'] = _kill = generate_set_str(node.pop('KILL', set()))
        node['EXPR'] = _expr = generate_set_str([str(x) for x in node.pop('EXPR', set())])
        node['title'] = "\n  ".join([obj.to_briltxt() if hasattr(obj, 'to_briltxt') else str(obj) for obj in node.pop('instructions', [])])
        node['title'] += f"\nGEN: { _gen }"
        node['title'] += f"\nKILL: { _kill }"
        node['title'] += f"\nEXPR: { _expr }"
        node['title'] += f"\nIN: { _in }"
        node['title'] += f"\nOUT: { _out }"
    return net
```
_\*Reference: https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/601e0e9ae2116bd59ef11847346e94e5bc639a0f/HW3/df_analysis.py#L367-L376_


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

