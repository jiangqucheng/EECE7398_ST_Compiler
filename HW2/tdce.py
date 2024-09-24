"""
Homework 2: Local Optimizations
Part 1
Implement 'trivial' dead code elimination that deletes instructions that are never used before they are reassigned.
"""

import sys
import json
from typing import List
from bril_model.form_blocks import form_blocks
from util import flatten
import bril_model as bm


def trivial_dce_pass(func: bm.BrilFunction) -> bool:
    """Remove instructions from `func` that are never used as arguments
    to any other instruction. Return a bool indicating whether we deleted
    anything.
    """
    blocks = list(form_blocks(func.instrs))

    # Find all the variables used as an argument to any instruction,
    # even once.
    used = set()
    for block in blocks:
        for instr in block:
            # Mark all the variable arguments as used.
            used.update(instr.args if instr.args else [])

    # Delete the instructions that write to unused variables.
    changed = False
    for block in blocks:
        # Avoid deleting *effect instructions* that do not produce a
        # result. The `'dest' in i` predicate is true for all the *value
        # functions*, which are pure and can be eliminated if their
        # results are never used.
        new_block = [instr for instr in block
                     if instr.dest is None or instr.dest in used]

        # Record whether we deleted anything.
        changed |= len(new_block) != len(block)

        # Replace the block with the filtered one.
        block[:] = new_block

    # Reassemble the function.
    func.set_instrs(flatten(blocks))

    return changed


def trivial_dce(func: bm.BrilFunction):
    """Iteratively remove dead instructions, stopping when nothing
    remains to remove.
    """
    # An exercise for the reader: prove that this loop terminates.
    while trivial_dce_pass(func):
        pass


def drop_killed_local(block: List[bm.BrilInstruction]) -> bool:
    """Delete instructions in a single block whose result is unused
    before the next assignment. Return a bool indicating whether
    anything changed.
    """
    # A map from variable names to the last place they were assigned
    # since the last use. These are candidates for deletion---if a
    # variable is assigned while in this map, we'll delete what the maps
    # point to.
    last_def = {}

    # Find the indices of droppable instructions.
    to_drop = set()
    for i, instr in enumerate(block):
        # Check for uses. Anything we use is no longer a candidate for
        # deletion.
        for var in (instr.args if instr.args else []):
            if var in last_def:
                del last_def[var]

        # Check for definitions. This *has* to happen after the use
        # check, so we don't count "a = a + 1" as killing a before using
        # it.
        if instr.dest:
            if instr.dest in last_def:
                # Another definition since the most recent use. Drop the
                # last definition.
                to_drop.add(last_def[instr.dest])
            last_def[instr.dest] = i

    # Remove the instructions marked for deletion.
    new_block = [instr for i, instr in enumerate(block)
                 if i not in to_drop]
    changed = len(new_block) != len(block)
    block[:] = new_block
    return changed


def drop_killed_pass(func: bm.BrilFunction):
    """Drop killed functions from *all* blocks. Return a bool indicating
    whether anything changed.
    """
    blocks = list(form_blocks(func.instrs))
    changed = False
    for block in blocks:
        changed |= drop_killed_local(block)
    func.set_instrs(flatten(blocks))
    return changed


def trivial_dce_plus(func: bm.BrilFunction):
    """Like `trivial_dce`, but also deletes locally killed instructions.
    """
    while trivial_dce_pass(func) or drop_killed_pass(func):
        pass


MODES = {
    'tdce': trivial_dce,
    'tdcep': trivial_dce_pass,
    'dkp': drop_killed_pass,
    'tdce+': trivial_dce_plus,
    'none': None,
}


def localopt():
    if len(sys.argv) > 1:
        modify_func = MODES[sys.argv[1]]
    else:
        modify_func = None

    # Apply the change to all the functions in the input program.
    bril_in_dict = json.load(sys.stdin)
    bbs = bm.BrilScript(raw=bril_in_dict)

    if modify_func:
    	for func in bbs.functions:
            modify_func(func)

    # Output the modified program.
    json.dump(bbs.dump(), sys.stdout, indent=2, sort_keys=True)


if __name__ == '__main__':
    localopt()
