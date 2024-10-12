# %% [markdown]
# # Playground - data flow graph 

# %%
print()
import os
import networkx as nx
import pyvis as pv
import matplotlib.pyplot as plt
from typing import Iterable, Tuple, Set, List, Dict, OrderedDict
import bril_model as bm
from bril_model.form_blocks import print_blocks, form_blocks


# usage: <this_script> ANALYSIS DEMO_BRIL_FILE [--save-dir=./save] 
#  - ANALYSIS: liveness, availability, busy
#  - DEMO_BRIL_FILE: path to the bril file
#  - SAVE_DIR: path to save the generated html files

import argparse
parser = argparse.ArgumentParser(description='Generate data flow graph for a bril script')
parser.add_argument('ANALYSIS', type=str, help='Analysis: [liveness, availability, busy]')
parser.add_argument('DEMO_BRIL_FILE', type=str, help='Path to the bril file')
parser.add_argument('--save-dir', type=str, default='./save', help='Path to save the generated html files')
args = parser.parse_args()

ANALYSIS = args.ANALYSIS.lower()
DEMO_BRIL_FILE = args.DEMO_BRIL_FILE
# how to get the save-dir value
SAVE_DIR = args.save_dir

# make sure args are allowed
correct = True
if ANALYSIS not in ['liveness', 'availability', 'busy']:
    print(f"Analysis <{ANALYSIS}> not supported")
    correct = False
if not os.path.exists(DEMO_BRIL_FILE):
    print(f"File <{DEMO_BRIL_FILE}> not found")
    correct = False
if not correct:
    # print help and exit
    parser.print_help()
    exit(1)

# DEMO_BRIL_FILE = "../bril/benchmarks/core/is-decreasing.bril"
# DEMO_BRIL_FILE = "../bril/benchmarks/core/hanoi.bril"
# DEMO_BRIL_FILE = "../bril/benchmarks/core/birthday.bril"
# DEMO_BRIL_FILE = "../bril/examples/test/df/fact.bril"
# DEMO_BRIL_FILE = "../bril/examples/test/df/cond.bril"
# DEMO_BRIL_FILE = "../bril/examples/test/df/cond-args.bril"
# DEMO_BRIL_FILE = "./example/in_class_example_2.bril"
# DEMO_BRIL_FILE = "./example/in_class_example_3.bril"

# ANALYSIS = "liveness"
# ANALYSIS = "availability"
# ANALYSIS = "busy"


# %%
print()

class Expr:
    """
    A Expr uniquely represents a computation in terms of sub-values.
    This is from HW2, but change `argnums` back to `args`
    """
    def __init__(self, op: str, args: List[str]):
        self.op = op
        if op in ['add', 'mul', 'and', 'or', 'eq']:
            self.args = sorted(args)
        self.args = args
    def __hash__(self):
        _hash_tuple = tuple([self.op, tuple(self.args)])
        return hash(_hash_tuple)
    def __eq__(self, other):
        return self.op == other.op and self.args == other.args
    def __repr__(self):
        return f"{__class__.__name__} {str(self)}"
    def __str__(self):
        return f"{self.op}({','.join(self.args)})"
    def __lt__(self, other):
        return hash(self) < hash(other)

# %%
print()
ENTRY_POINT_NAME = 'ENTRY\nPOINT'
RETURN_POINT_NAME = 'RETURN\nPOINT'

def iter_func_blocks(bs: bm.BrilScript) -> Iterable[Tuple[bm.BrilFunction, OrderedDict[bm.BrilInstruction_Label, List[bm.BrilInstruction]]]]:
    for each_func in bs.functions:
        block_dict: OrderedDict[bm.BrilInstruction_Label, List[bm.BrilInstruction]] = {}
        anonymous_id = 0
        for each_block in form_blocks(each_func.instrs):
            this_block_label = None
            if isinstance(each_block[0], bm.BrilInstruction_Label):
                this_block_label = each_block[0]
                block_dict[this_block_label] = each_block[1:]
            else:
                this_block_label = bm.BrilInstruction_Label(dict(label='_f{}._anon{}'.format(str(hash(each_func.name)%1000).zfill(3), anonymous_id)))
                block_dict[this_block_label] = each_block[:]
                anonymous_id += 1
        yield (each_func, block_dict)

def update_to_graph(bbs: bm.BrilScript, app_graph_dict: Dict[bm.BrilFunction, Tuple[nx.DiGraph, Dict[bm.BrilInstruction_Label, List[bm.BrilInstruction]]]]):
    for each_func, block_dict in iter_func_blocks(bbs):
        print("Function: {}".format(each_func.name))
        fdg = nx.DiGraph()  # function directed graph
        last_label = None
        is_first = True
        for each_label, each_block in block_dict.items():
            fdg.add_node(each_label.label, instructions=[each_label]+each_block)
            if last_label:
                fdg.add_edge(last_label.label, each_label.label, reason='[fallthrough]')
            elif is_first:
                fdg.add_edge(ENTRY_POINT_NAME, each_label.label, reason='[enter]')
                is_first = False
            
            final_instr = each_block[-1] if each_block else None
            if final_instr is None:
                last_label = each_label
            else:
                if final_instr.op in ['jmp', 'br']:
                    for redirect_instr_to_dest in final_instr.labels:
                        fdg.add_edge(each_label.label, redirect_instr_to_dest, reason=final_instr.to_briltxt())
                    last_label = None
                elif final_instr.op in ['ret']:
                    fdg.add_edge(each_label.label, RETURN_POINT_NAME, reason=final_instr.to_briltxt())
                    last_label = None
                else:
                    last_label = each_label
        app_graph_dict[each_func] = (fdg, block_dict)


# load the bril script
bbs = bm.BrilScript(script_name=os.path.basename(DEMO_BRIL_FILE), file_dir=os.path.dirname(DEMO_BRIL_FILE))
app_graph: Dict[bm.BrilFunction, Tuple[nx.DiGraph, Dict[bm.BrilInstruction_Label, List[bm.BrilInstruction]]]] = {}
update_to_graph(bbs, app_graph)

# %%
print()
# for each basic block, generate set of variables and expressions that:
# 1. var used before defined
# 2. var modified in the block
# 3. expr available at the end of the block
# Mark used before defined variables as set(GEN), modified variables as set(KILL), available expressions as set(EXPR)
# GEN = {v | v is used before defined}
# KILL = {v | v is modified}
# EXPR = {e | e is available at the end of the block} 

def get__args_used_before_assign__assigned__calc_expr_available_at_bb_end(instrs: List[bm.BrilInstruction]) -> Tuple[Set[str],Set[str],Set[Expr]]:
    """
    Given a list of instructions, return the set of variables that are used before defined and the set of variables that are modified.
    This is from HW2, but modified to return the sets instead of printing them.
    """
    used_first: Set[str] = set()
    written: Set[str] = set()
    avail_exprs: Set[Expr] = set()
    for instr in instrs:
        used_first.update(set(instr.args if instr.args else []) - written)
        if instr.dest:
            # check if the dest was used in generating any of the expressions, if so, remove it from exprs
            for expr in list(avail_exprs):
                if instr.dest in expr.args:
                    avail_exprs.remove(expr)
            written.add(instr.dest)
            if instr.args and instr.op not in ['id', 'const', 'call']:
                avail_exprs.add(Expr(instr.op, instr.args))
    return used_first, written, avail_exprs

def gen_kill_expr_sets(block: List[bm.BrilInstruction]) -> Tuple[Set[str],Set[str],Set[Expr]]:
    return get__args_used_before_assign__assigned__calc_expr_available_at_bb_end(block)

def update_gen_kill_sets(app_graph: Dict[bm.BrilFunction, Tuple[nx.DiGraph, Dict[bm.BrilInstruction_Label, List[bm.BrilInstruction]]]]):
    for _, (fdg, _) in app_graph.items():
        for each_node, each_node_data in fdg.nodes(data=True):
            each_block: List[bm.BrilInstruction] = each_node_data.get('instructions', None)
            _gen, _kill, _expr = gen_kill_expr_sets(each_block) if each_block else (set(), set(), set())
            fdg.nodes[each_node]['GEN'] = _gen
            fdg.nodes[each_node]['KILL'] = _kill
            fdg.nodes[each_node]['EXPR'] = _expr

# update the GEN, KILL, EXPR sets for each basic block
# this is the first step in the dataflow analysis
# these sets are like properties of the nodes in the graph
# will not change during the analysis for IN and OUT sets
update_gen_kill_sets(app_graph)

# %%
print()
# some helper functions to get the sets of a node
from typing import Callable


_get_node_gen_set = lambda fdg, node_name: fdg.nodes[node_name].get('GEN', set())
_get_node_kill_set = lambda fdg, node_name: fdg.nodes[node_name].get('KILL', set())
_get_node_expr_set = lambda fdg, node_name: fdg.nodes[node_name].get('EXPR', set())
_get_node_in_set = lambda fdg, node_name: fdg.nodes[node_name].get('IN', set())
_get_node_out_set = lambda fdg, node_name: fdg.nodes[node_name].get('OUT', set())
_get_node_pred_set = lambda fdg, node_name: set(fdg.predecessors(node_name))
_get_node_succ_set = lambda fdg, node_name: set(fdg.successors(node_name))

def _fdg_update_bare_bone(specific_analysis_func: Callable[[nx.DiGraph, str], Tuple[Set[str], Set[str]]], fdg: nx.DiGraph) -> bool:
    # here we extract the common part of the analysis
    has_changed = False
    for this_node, _ in fdg.nodes(data=True):
        _print_this_node_name = this_node.replace('\n', '\\n')
        _in, _out = specific_analysis_func(fdg, this_node)
        print(f"Node: {_print_this_node_name}, IN: {_in}, OUT: {_out}")
        if _in != _get_node_in_set(fdg, this_node) or _out != _get_node_out_set(fdg, this_node):
            fdg.nodes[this_node]['IN'] = _in
            fdg.nodes[this_node]['OUT'] = _out
            has_changed = True
    return has_changed

def _fdg_update_internal_liveness_sets(fdg: nx.DiGraph, this_node: str) -> Tuple[Set[str], Set[str]]:
    """
        this.gen = {v | v is used before defined here}
        this.kill = {v | v is assigned here}
        IN = this.gen + (OUT - this.kill)
        OUT = union(successors' IN)
    """
    _print_this_node_name = this_node.replace('\n', '\\n')
    _temp_succ_req = [_get_node_in_set(fdg, each_succ_node) for each_succ_node in _get_node_succ_set(fdg, this_node)]
    _out: Set[str] = set.union(*_temp_succ_req) if _temp_succ_req else set()
    print(f"Node: {_print_this_node_name}, Succ: {_get_node_succ_set(fdg, this_node)}=>{_temp_succ_req}, OUT: {_out}")
    _in: Set[str] = set.union(_get_node_gen_set(fdg, this_node), set.difference(_out, _get_node_kill_set(fdg, this_node)))
    return _in, _out

def _fdg_update_internal_availability_sets(fdg: nx.DiGraph, this_node: str) -> Tuple[Set[Expr], Set[Expr]]:
    """
        this.exprs = {e | e is available at the end of the block}
        IN = intersection(predeccessors' OUT)
        OUT = (IN + this.exprs) - OUT(expr: any(var modified here exist in expr))
    """
    _print_this_node_name = this_node.replace('\n', '\\n')
    _temp_pred_give = [_get_node_out_set(fdg, each_pred_node) for each_pred_node in _get_node_pred_set(fdg, this_node)]
    _in: Set[Expr] = set.intersection(*_temp_pred_give) if _temp_pred_give else set()
    print(f"Node: {_print_this_node_name}, Pred: {_get_node_pred_set(fdg, this_node)}=>{_temp_pred_give}, IN: {_in}")
    # gatter all exprs that were computed before the end of this block 
    _out: Set[Expr] = set.union(_get_node_in_set(fdg, this_node), _get_node_expr_set(fdg, this_node))
    # remove such expr that include variables that were modified in this block
    _out = set([each_expr for each_expr in _out if not set.intersection(set(each_expr.args), _get_node_kill_set(fdg, this_node))])
    return _in, _out

def _fdg_update_internal_busy_sets(fdg: nx.DiGraph, this_node: str) -> Tuple[Set[Expr], Set[Expr]]:
    """
        IN = (OUT - OUT(expr: any(var modified here exist in expr)) + this.exprs
        OUT = intersection(successors' IN)
    """
    _print_this_node_name = this_node.replace('\n', '\\n')
    _temp_succ_req = [_get_node_in_set(fdg, each_succ_node) for each_succ_node in _get_node_succ_set(fdg, this_node)]
    _out: Set[Expr] = set.intersection(*_temp_succ_req) if _temp_succ_req else set()
    print(f"Node: {_print_this_node_name}, Succ: {_get_node_succ_set(fdg, this_node)}=>{_temp_succ_req}, OUT: {_out}")
    # remove such expr that include variables that were modified in this block
    _in: Set[Expr] = set([each_expr for each_expr in _out if not set.intersection(set(each_expr.args), _get_node_kill_set(fdg, this_node))])
    # add all exprs that are computed in this block
    _in = set.union(_in, _get_node_expr_set(fdg, this_node))
    return _in, _out

ANALYSIS_FUNC = {
    'liveness': _fdg_update_internal_liveness_sets,
    'availability': _fdg_update_internal_availability_sets,
    'busy': _fdg_update_internal_busy_sets,
}

def update_analysis_sets(analysis_type_str: str , app_graph: Dict[bm.BrilFunction, Tuple[nx.DiGraph, Dict[bm.BrilInstruction_Label, List[bm.BrilInstruction]]]]):
    analysis_func = ANALYSIS_FUNC.get(analysis_type_str, None)
    if not analysis_func:
        print(f"Analysis <{analysis_type_str}> not supported")
        return
    has_changed = True
    while has_changed:
        has_changed = False
        print(f"Updating {analysis_type_str} sets")
        for _, (fdg, _) in app_graph.items():
            has_changed |= _fdg_update_bare_bone(analysis_func, fdg)
        print()

update_analysis_sets(ANALYSIS, app_graph)

# %%
print()
CONST_EMPTY_STR = '\u2205'

def generate_set_str(showing_set: set) -> str:
    return '{' + ','.join([x if isinstance(x, str) else str(x) for x in sorted(showing_set)]) + '}' if showing_set else CONST_EMPTY_STR

def dump_into_pv_graph(fdg: nx.DiGraph) -> pv.network.Network:
    # Plot with pyvis
    net = pv.network.Network(
        directed=True,
        neighborhood_highlight=True,
        notebook=True,
        cdn_resources="remote", 
        height="100vh",
        width="100vw",
    )

    # net.show_buttons(['nodes', 'edges', 'layout', 'interaction', 'manipulation', 'physics', 'selection', 'renderer']) # Show part 3 in the plot (optional)
    net.from_nx(fdg) # Create directly from nx graph
    _net_node_name2idx: Dict[str, int] = {node['id']: idx for idx, node in enumerate(net.nodes)}
    _map_node_name2idx = lambda node_name: _net_node_name2idx.get(node_name, None)
    _get_node_by_name = lambda node_name: net.nodes[_map_node_name2idx(node_name)] if _map_node_name2idx(node_name) is not None else dict()

    # net.show_buttons(['physics',])

    net.options.interaction.hover = True
    net.options.physics.use_force_atlas_2based(dict(
        gravity=-100,
        spring_strength=0.05,
        central_gravity=0.01,
        spring_length=200,
        damping=0.45,
        overlap=0,
    ))

    # Traverse the net nodes of PyVis and convert the data
    for node in net.nodes:
        node['IN'] = _in = generate_set_str(node.pop('IN', set()))
        node['OUT'] = _out = generate_set_str(node.pop('OUT', set()))
        node['GEN'] = _gen = generate_set_str(node.pop('GEN', set()))
        node['KILL'] = _kill = generate_set_str(node.pop('KILL', set()))
        node['EXPR'] = _expr = generate_set_str([str(x) for x in node.pop('EXPR', set())])

        node['title'] = ''
        if 'instructions' in node:
            # remove 'data' key from node, and set 'title' key to the string representation of the data
            node['title'] = "\n  ".join([obj.to_briltxt() if hasattr(obj, 'to_briltxt') else str(obj) for obj in node.pop('instructions', [])])
            node['shape'] = 'box'
        node['title'] += "\n"
        node['title'] += f"\nGEN: { _gen }"
        node['title'] += f"\nKILL: { _kill }"
        node['title'] += f"\nEXPR: { _expr }"
        node['title'] += f"\nIN: { _in }"
        node['title'] += f"\nOUT: { _out }"

        # title layout change (word replace):
        #  strip: remove leading/trailing spaces, tabs, newlines, and carriage returns
        #  double return -> dash line
        #  double space -> full corner single space
        node['title'] = node['title'].strip(' \t\n\r').replace('\n\n', '\n--------\n').replace('  ', '\u3000')

        # node['label'] = f"IN: {_in}" + '\n' + node['label'] + '\n' + f"OUT: {_out}"

        if node['id'] in (ENTRY_POINT_NAME, RETURN_POINT_NAME):
            node['color'] = 'grey'
            node['shape'] = 'circle'

    for edge in net.edges:
        _reason = edge.pop('reason', None)
        if _reason:
            edge['label'] = _reason
        _src_node, _dst_node = _get_node_by_name(edge['from']), _get_node_by_name(edge['to'])
        if _src_node and _dst_node and 'OUT' in _src_node and 'IN' in _dst_node:
            src_id, src_out, dst_id, dst_in = _src_node['id'], _src_node['OUT'], _dst_node['id'], _dst_node['IN']
            if src_out == CONST_EMPTY_STR: src_out = dst_in
            if dst_in == CONST_EMPTY_STR: dst_in = src_out
            new_label = f"{src_id}.OUT:{src_out}\n{dst_id}.IN:{dst_in}" if src_out != dst_in else src_out
            edge['title'] = edge.get('title', "") + edge.get('label', "")  # move label to popup title
            edge['label'] = new_label  # set new label
    
    return net

# Safe linux fs name
safe_fs_name = lambda raw_string: "".join(c if c.isalnum() or c in (' ', '.', '_') else '_' for c in raw_string)

for each_func in bbs.functions:
    # Remove illegal characters for Linux filesystem
    save_dir = os.path.join(SAVE_DIR, safe_fs_name(bbs.script_name), ANALYSIS)
    save_file = f"{safe_fs_name(each_func.name)}.html"
    # get the function directed graph
    fdg, _ = app_graph.get(each_func)
    # mkdir -p ./save_dir
    os.makedirs(f"./{save_dir}", exist_ok=True)
    # save to html
    dump_into_pv_graph(fdg).save_graph(os.path.join(save_dir, save_file))

# %%
print()
print_blocks(bbs)


