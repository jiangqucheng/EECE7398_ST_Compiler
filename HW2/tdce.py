"""
Homework 2: Local Optimizations
Part 1
Implement 'trivial' dead code elimination that deletes instructions that are never used before they are reassigned.
"""

import sys
import json
from typing import Any, Dict, List
from bril_model.form_blocks import form_blocks
import bril_model as bm


def trivial_dce_once(func: bm.BrilFunction) -> bool:
    # collect all used variables
    used = set()
    for instr in func.instrs:
        used.update(instr.args if instr.args else [])

    # mark instructions that are not used
    changed = False
    for instr in func.instrs:
        if instr.dest and instr.dest not in used:
            instr.mark_delete()
            changed = True

    # Update the function's instruction list. 
    func.set_instrs([instr for instr in func.instrs if instr.is_deleted is not True])

    return changed


def trivial_dce(func: bm.BrilFunction):
    # Run the function-level DCE pass until no more changes are made.
    while trivial_dce_once(func):
        continue


def _block_mark_reassign_before_use(block: List[bm.BrilInstruction]) -> bool:
    """
    Inside a single BB, delete instructions that dest is reassigned before consumed.
    """
    recent_assign_not_used: Dict[str, bm.BrilInstruction] = {}
    changed = False

    # Find the indices of droppable instructions.
    for instr in block:
        if instr.is_deleted:
            continue
        # check consume before produce, because of case: a=a+1;
        # this instr consumes ...
        if instr.args:
            for var in instr.args:
                if var in recent_assign_not_used:
                    del recent_assign_not_used[var]
        # this instr produces ...
        if instr.dest:
            if instr.dest in recent_assign_not_used:
                # reassigning to dest before last value is used.
                # mark the instr that produces last value for deletion.
                recent_assign_not_used[instr.dest].mark_delete()
                changed = True
            # update the most recent assignment
            recent_assign_not_used[instr.dest] = instr
    
    return changed


def rm_reassign_before_use(func: bm.BrilFunction):
    """
    Remove instructions that are reassigned before they are used.
    """
    blocks = list(form_blocks(func.instrs))
    
    changed = False
    for block in blocks:
        changed |= _block_mark_reassign_before_use(block)
    
    # Update the function's instruction list. 
    func.set_instrs([instr for instr in func.instrs if instr.is_deleted is not True])
    
    return changed


def trivial_dce_plus(func: bm.BrilFunction):
    """
    Do function-level DCE pass & reassign before use pass.
    """
    while trivial_dce_once(func) or rm_reassign_before_use(func):
        pass


MODES = {
    'tdce': trivial_dce,                # do function-level DCE until no more changes
    'tdce1': trivial_dce_once,          # do function-level DCE once
    'raby': rm_reassign_before_use,     # remove reassign before use
    'tdce+': trivial_dce_plus,          # do function-level DCE and remove reassign before use
    'none': None,                       # nothing
}


if __name__ == '__main__':
    # Parse the command-line argument.
    if len(sys.argv) == 2:
        modify_func = MODES[sys.argv[1]]
    elif len(sys.argv) == 1:
        modify_func = None
    else:
        raise ValueError("Usage: python3 tdce.py [tdce|tdce1|raby|tdce+|none] < input.bril.json > output.bril.json")

    # Read the input program, and create a BrilScript object.
    bril_in_dict = json.load(sys.stdin)
    bbs = bm.BrilScript(raw=bril_in_dict)

    # Apply the change to all the functions in the input program.
    if modify_func:
    	for func in bbs.functions:
            modify_func(func)

    # Output the modified program.
    json.dump(bbs.dump(), sys.stdout, indent=2, sort_keys=True)
