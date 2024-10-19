# %% [markdown]
# # Playground - data flow graph 

# %%
import os
import networkx as nx
import pyvis as pv
import matplotlib.pyplot as plt
import graphviz as gv
from typing import Iterable, Tuple, Set, List, Dict, OrderedDict, Optional
import bril_model as bm
from bril_model.form_blocks import form_blocks
from hashlib import sha256
fast_hash = lambda str: sha256(str).hexdigest()[:3]


# usage: <this_script> DEMO_BRIL_FILE [--save-dir=./save | --mute-output] 

import argparse
parser = argparse.ArgumentParser(description='Generate CFG with dominance frontier and Dominator-Tree for a bril script')
parser.add_argument('DEMO_BRIL_FILE', type=str, help='Path to the bril file')
parser.add_argument('--save-dir', type=str, default='./save', help='Path to save the generated html files')
parser.add_argument('--mute-output', action='store_true', help='Mute the output of the graphviz render', default=False)
args = parser.parse_args()

DEMO_BRIL_FILE = args.DEMO_BRIL_FILE
SAVE_DIR = args.save_dir
MUTE_OUTPUT = args.mute_output

# DEMO_BRIL_FILE = "../bril/examples/test/dom/loopcond.bril"
# DEMO_BRIL_FILE = "../bril/examples/test/dom/while.bril"

# %%
# make sure args are allowed
args_correct = True
if not os.path.exists(DEMO_BRIL_FILE):
    print(f"File <{DEMO_BRIL_FILE}> not found")
    args_correct = False
if not args_correct:
    # print help and exit
    parser.print_help()
    exit(1)

# %%
ENTRY_POINT_NAME = 'ENTRY'
RETURN_POINT_NAME = 'RETURN'

class BasicBlock():
    def __init__(self, label: bm.BrilInstruction_Label, instrs: List[bm.BrilInstruction]):
        if not isinstance(label, bm.BrilInstruction_Label):
            raise TypeError(f"Expected label, got {type(label)}")
        if label not in instrs:
            instrs.insert(0, label)
        self.instrs = instrs
        self.succ: Set[BasicBlock] = set()
        self.pred: Set[BasicBlock] = set()
    
    @property
    def label(self):
        return self.instrs[0]
    
    def __hash__(self) -> int:
        return hash(self.label)
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, BasicBlock):
            return False
        return self.label == o.label
    def __lt__(self, o: object) -> bool:
        if not isinstance(o, BasicBlock):
            return False
        # return block is always the last one
        if self.label.label == RETURN_POINT_NAME: return False
        if o.label.label == RETURN_POINT_NAME: return True
        # entry block is always the first one
        if self.label.label == ENTRY_POINT_NAME: return True
        if o.label.label == ENTRY_POINT_NAME: return False
        return self.label < o.label

    def __str__(self):
        if self.label.label in {ENTRY_POINT_NAME, RETURN_POINT_NAME}: return self.label.label
        _instrs = '\n  '.join([x.to_briltxt() for x in self.instrs[1:]])
        if _instrs:
            _instrs = f"\n  {_instrs}"
        return f"{self.label.to_briltxt()}{_instrs}"
    def __repr__(self):
        return f"{self.__class__.__name__} :: {self.label.to_briltxt()}..[{len(self.instrs) - 1}]"

# %%
def iter_func_blocks(bs: bm.BrilScript) -> Iterable[Tuple[bm.BrilFunction, List[BasicBlock]]]:
    for each_func in bs.functions:
        bbs: List[BasicBlock] = list()
        anonymous_id = 0
        for each_block in form_blocks(each_func.instrs):
            this_block_label: bm.BrilInstruction_Label = None
            if isinstance(each_block[0], bm.BrilInstruction_Label):
                this_block_label = each_block[0]
            else:
                this_block_label = bm.BrilInstruction_Label(dict(label='_f{}._anon{}'.format(fast_hash(each_func.name.encode()), anonymous_id)))
                anonymous_id += 1
            bbs.append(BasicBlock(this_block_label, each_block))
        yield (each_func, bbs)

def generate_func_cfg_dict(bscript: bm.BrilScript) -> Dict[bm.BrilFunction, List[BasicBlock]]:
    app_bbs_dict: OrderedDict[bm.BrilFunction, List[BasicBlock]] = {}
    for each_func, basic_blocks in iter_func_blocks(bscript):
        # print("Function: {}".format(each_func.name))
        entry_bb = BasicBlock(bm.BrilInstruction_Label(dict(label=ENTRY_POINT_NAME)), [])
        return_bb = BasicBlock(bm.BrilInstruction_Label(dict(label=RETURN_POINT_NAME)), [])
        prev_bb: Optional[BasicBlock] = None
        is_first: bool = True
        for each_bb in basic_blocks:
            if prev_bb:
                # reason: fallthrough edge
                prev_bb.succ.add(each_bb)
                each_bb.pred.add(prev_bb)
            elif is_first:
                # reason: entry edge
                entry_bb.succ.add(each_bb)
                each_bb.pred.add(entry_bb)
                is_first = False
            
            # get last instruction if exists
            final_instr = each_bb.instrs[-1] if each_bb.instrs else None
            if final_instr is None:
                # empty block, skip
                prev_bb = each_bb
            elif final_instr.op in ['jmp', 'br']:
                # reaching control flow instruction
                for redirect_instr_to_bb_label in final_instr.labels:
                    next_bb = next((bb for bb in basic_blocks if bb.label.label == redirect_instr_to_bb_label), None)
                    if next_bb is None:
                        raise ValueError(f"Cannot find block with label {redirect_instr_to_bb_label}")
                    # reason: control flow edge
                    each_bb.succ.add(next_bb)
                    next_bb.pred.add(each_bb)
                prev_bb = None
            elif final_instr.op in ['ret']:
                # reaching return instruction
                # reason: return edge
                each_bb.succ.add(return_bb)
                return_bb.pred.add(each_bb)
                prev_bb = None
                # explicit return block, no fallthrough
            else:
                # normal instruction, prepare for fallthrough
                prev_bb = each_bb
        # check if last block has no fallthrough
        if prev_bb:
            # reason: return edge
            prev_bb.succ.add(return_bb)
            return_bb.pred.add(prev_bb)
        # add entry/return block
        basic_blocks.insert(0, entry_bb)
        basic_blocks.append(return_bb)
        app_bbs_dict[each_func] = basic_blocks
    return app_bbs_dict

def getBasicBlockByLabel(bb_list: List[BasicBlock], label: str) -> Optional[BasicBlock]:
    return next((bb for bb in bb_list if bb.label.label == label), None)

# %%
def generate_dom_dict(bbs: List[BasicBlock]) -> dict[BasicBlock, set[BasicBlock]]:
    # Initialize dominator sets for each block
    # Initially, every block dominates every other block
    dom: Dict[BasicBlock, Set[BasicBlock]] = {bb: set(bbs) for bb in bbs}
    # The entry block only dominates itself
    bb_entry = getBasicBlockByLabel(bbs, ENTRY_POINT_NAME)
    dom[bb_entry] = set([bb_entry])

    changed: bool = True
    while changed:
        changed = False
        for each_bb in bbs:
            if each_bb == bb_entry: continue
            # The dominator set of a bb is the intersection of the dominator sets of its predecessors
            this_bb_dom = set.intersection(*[dom[each_pred] for each_pred in each_bb.pred] or [set()])
            # The dominator set of a bb should includes itself
            this_bb_dom.add(each_bb)
            # Update if changed
            if dom[each_bb] != this_bb_dom:
                dom[each_bb] = this_bb_dom
                changed = True
    return dom

# get the last dom of a given block
def get_lease_superset_dom(dom_dict: dict[BasicBlock, set[BasicBlock]], bb: BasicBlock) -> Optional[BasicBlock]:
    return next((test_dom for test_dom in dom_dict[bb] if ((dom_dict[bb] - dom_dict[test_dom]) == set([bb]))), None)

# get the dom frontiers of a given block. (One-liner version, the well-commented version is hidden in previous commits)
def get_dom_frontier(dom: Dict[BasicBlock, Set[BasicBlock]], bb: BasicBlock) -> Set[BasicBlock]:
    return set([test_with_bb for test_with_bb in dom.keys() if (bb not in dom[test_with_bb] or bb == test_with_bb) and (bb in set.union(*[dom[each_tbp] for each_tbp in test_with_bb.pred] or [set()]))])


# %%
def get_style_attrs(bb: BasicBlock) -> dict:
    _addi_attrs = dict()
    if bb.label.label in [ENTRY_POINT_NAME, RETURN_POINT_NAME]:
        _addi_attrs['shape'] = 'doublecircle'
        _addi_attrs['style'] = 'filled'
        _addi_attrs['fillcolor'] = 'lightgray'
    else:
        _addi_attrs['shape'] = 'box'
    return _addi_attrs

def create_graphviz_dot_node(dot: gv.Digraph, func: bm.BrilFunction, bb: BasicBlock, **kw_args) -> None:
    dot.node(f"FUNC_{func.name}_NODE_{bb.label.label}", label=f"{bb}", **get_style_attrs(bb), **kw_args)

def create_graphviz_dot_edge(dot: gv.Digraph, func: bm.BrilFunction, from_bb: BasicBlock, to_bb: BasicBlock, **kw_args) -> None:
    dot.edge(f"FUNC_{func.name}_NODE_{from_bb.label.label}", f"FUNC_{func.name}_NODE_{to_bb.label.label}", **kw_args)

def create_graphviz_dot(app_graph: Dict[bm.BrilFunction, List[BasicBlock]]) -> Tuple[gv.Digraph, gv.Digraph]:
    dot_cfg = gv.Digraph('CFG', comment='Control Flow Graph')
    dot_domt = gv.Digraph('DOMTREE', comment='Dominator Tree')
    for each_func, bbs in app_graph.items():
        _func_show_str = str(each_func).replace('\t', '  ')
        print(f" {_func_show_str} ".center(80, '='))
        dom = generate_dom_dict(bbs)
        _max_bb_label_len = max([len(bb.label.label) for bb in bbs])

        # each func is a subgraph
        with dot_cfg.subgraph(name=f"cluster_{each_func.name}") as dot_cfg_func, dot_domt.subgraph(name=f"cluster_{each_func.name}") as dot_domt_func:
            dot_cfg_func.attr(label=each_func.name)
            dot_cfg_func.attr(color='#f7f7f7')
            dot_cfg_func.attr(style='filled')
            dot_cfg_func.attr(rankdir='TB')
            dot_domt_func.attr(label=each_func.name)
            dot_domt_func.attr(color='#f7f7f7')
            dot_domt_func.attr(style='filled')
            dot_domt_func.attr(rankdir='TB')

            print(" Dom-Front ".center(80, '-'))
            # generate cfg dot graph
            for each_bb in bbs:
                dom_frontiers = get_dom_frontier(dom, each_bb)
                print(f"{each_bb.label.label.ljust(_max_bb_label_len)} : {', '.join([x.label.label for x in sorted(dom_frontiers)])}")
                create_graphviz_dot_node(dot_cfg_func, each_func, each_bb)
                for each_df in dom_frontiers:
                    create_graphviz_dot_edge(dot_cfg_func, each_func, each_bb, each_df, style='dashed', color='#66ccff', label='DF', fontsize='10', fontcolor='#66ccff', constraint='false')
                for each_succ in each_bb.succ:
                    create_graphviz_dot_edge(dot_cfg_func, each_func, each_bb, each_succ)

            # generate domt dot graph
            print(" Dom & Dom-Tree ".center(80, '-'))
            for each_bb in dom.keys():
                least_superset_dom = get_lease_superset_dom(dom, each_bb)
                print(f"{each_bb.label.label.ljust(_max_bb_label_len)} <- {(least_superset_dom.label.label if least_superset_dom else '[ROOT]').ljust(_max_bb_label_len)} : {', '.join([x.label.label for x in sorted(dom[each_bb])])}")
                create_graphviz_dot_node(dot_domt_func, each_func, each_bb)
                if least_superset_dom:
                    create_graphviz_dot_edge(dot_domt_func, each_func, least_superset_dom, each_bb)
            
            # print the script in briltxt format for reference
            print(" Script ".center(80, '-'))
            for each_bb in bbs:
                for each_instr in each_bb.instrs:
                    print( ("" if isinstance(each_instr, bm.BrilInstruction_Label) else "  ") + each_instr.to_briltxt())
            
            print()
    return dot_cfg, dot_domt


# %%
# load the bril script
bscript = bm.BrilScript(script_name=os.path.basename(DEMO_BRIL_FILE), file_dir=os.path.dirname(DEMO_BRIL_FILE))
print(bscript)
app_graph: Dict[bm.BrilFunction, List[BasicBlock]] = generate_func_cfg_dict(bscript)
# print("Functions: {}".format(', '.join([f"[{idx}]={x.name}" for idx, x in enumerate(app_graph.keys())])))

print()
dot_cfg, dot_domt = create_graphviz_dot(app_graph)

if MUTE_OUTPUT:
    exit(0)

# Finally, create the save directory if not exists, and save the generated dot files
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

_gv_ret = dot_cfg.render(os.path.join(SAVE_DIR, bscript.script_name+".cfg.gv"), view=False)
print(_gv_ret)
_gv_ret = dot_domt.render(os.path.join(SAVE_DIR, bscript.script_name+".domt.gv"), view=False)
print(_gv_ret)
