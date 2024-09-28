"""
Homework 2: Local Optimizations
Part 2
Implement local value numbering.
"""

import sys
import json
from typing import Any, Dict, List, Optional, Set, Tuple
from bril_model.form_blocks import form_blocks, print_blocks
import bril_model as bm

class Expr:
    """
    A Expr uniquely represents a computation in terms of sub-values.
    """
    def __init__(self, op: str, argnums: List[int]):
        self.op = op
        if op in ['add', 'mul', 'and', 'or', 'eq']:
            self.argnums = sorted(argnums)
        self.argnums = argnums
    def __hash__(self):
        _hash_tuple = tuple([self.op, tuple(self.argnums)])
        # _hash_str = f"{self.op}"
        # if self.argnums:
        #     _hash_str += '_['+','.join(self.argnums)+']'
        return hash(_hash_tuple)
    def __eq__(self, other):
        return self.op == other.op and self.argnums == other.argnums



class IdxDict(dict):
    def __init__(self, init={}):
        super(IdxDict, self).__init__(init)
        self._curr_idx = -1

    def _new_idx(self) -> int:
        self._curr_idx = self._curr_idx + 1
        return self._curr_idx

    def assign(self, key) -> int:
        # when doing assign, get the local value number (idx) for the var
        idx = self._new_idx()
        self[key] = idx
        return idx

def args_use_before_assign(instrs: List[bm.BrilInstruction]) -> Set[str]:
    read = set()
    written = set()
    for instr in instrs:
        read.update(set(instr.args if instr.args else []) - written)
        written.add(instr.dest)
    return read

FOLDABLE_OPS = {
    'add': lambda a, b: a + b,
    'mul': lambda a, b: a * b,
    'sub': lambda a, b: a - b,
    'div': lambda a, b: a // b,
    'gt': lambda a, b: a > b,
    'lt': lambda a, b: a < b,
    'ge': lambda a, b: a >= b,
    'le': lambda a, b: a <= b,
    'ne': lambda a, b: a != b,
    'eq': lambda a, b: a == b,
    'or': lambda a, b: a or b,
    'and': lambda a, b: a and b,
    'not': lambda a: not a
}

def fold(num2const: Dict[int, int], expr: Expr) -> Optional[int]:
    if expr.op in FOLDABLE_OPS:
        try:
            const_args = [num2const[n] for n in expr.argnums]
            return FOLDABLE_OPS[expr.op](*const_args)
        except KeyError:  # At least one argument is not a constant.
            if expr.op in {'eq', 'ne', 'le', 'ge'} and \
               expr.argnums[0] == expr.argnums[1]:
                # Equivalent arguments may be evaluated for equality.
                # E.g. `eq x x`, where `x` is not a constant evaluates
                # to `true`.
                return expr.op != 'ne'

            if expr.op in {'and', 'or'} and \
               any(v in num2const for v in expr.argnums):
                # Short circuiting the logical operators `and` and `or`
                # for two cases: (1) `and x c0` -> false, where `c0` a
                # constant that evaluates to `false`. (2) `or x c1`  ->
                # true, where `c1` a constant that evaluates to `true`.
                const_val = num2const[expr.argnums[0]
                                      if expr.argnums[0] in num2const
                                      else expr.argnums[1]]
                if (expr.op == 'and' and not const_val) or \
                   (expr.op == 'or' and const_val):
                    return const_val
            return None
        except ZeroDivisionError:  # If hit a dynamic error, bail!
            return None
    else:
        return None


def lookup_expr_num(expr2num: Dict[Expr, int], expr: Expr) -> int:
    # handle the case of `id` op
    return expr2num.get(expr) if expr.op != 'id' else expr.argnums[0]

def block_lvn_mark(block: List[bm.BrilInstruction]):
    # Current block-index of each defined variable.
    var2idx: Dict[str, int] = IdxDict()

    # The canonical variable holding a given value. Every time we're
    # forced to compute a new value, we'll keep track of it here so we
    # can reuse it later.
    expr2num: Dict[Expr, int] = {}

    # The *canonical* variable name holding a given numbered value.
    # There is only one canonical variable per value number (so this is not the inverse of var2num). To make matters even more complicated, we will also keep a *list* of possible names here, where the first is the canonical one to use. This is only relevant when doing copy-propagation, and it helps with situations where a copy-propagated variable is later "clobbered" so we can fall back to a different variable holding the same value.
    expr_value_assigned_in_vars: Dict[int, List[str]] = {}

    # Track constant values for values assigned with `const`.
    num2const: Dict[int, int] = {}

    # Initialize the table with numbers for input variables. These variables are their own canonical source.
    for var in args_use_before_assign(block):
        idx = var2idx.assign(var)
        expr_value_assigned_in_vars[idx] = [var]

    # Mark if instr is last assignment to its dest variable
    __got_assigned_after = set()
    for instr in reversed(list(block)):
        instr.is_last_assign_to_dest = True if (instr.dest and instr.dest not in __got_assigned_after) else False
    del __got_assigned_after

    for instr in block:
        # Look up the value numbers for all variable arguments,
        # generating new numbers for unseen variables.
        argvars = instr.args if instr.args else []
        argnums: Tuple[int] = tuple(var2idx[var] for var in argvars)

        # Update argument variable names to canonical variables.
        instr.args = [expr_value_assigned_in_vars[n][0] for n in argnums] if instr.args is not None else None

        if instr.dest:
            for each_expr_value_assigned_in_var_list in expr_value_assigned_in_vars.values():
                if instr.dest in each_expr_value_assigned_in_var_list:
                    # `instr.dest` is no longer the place holder for the value
                    # remove the variable from the list, since 
                    each_expr_value_assigned_in_var_list.remove(instr.dest)

        # Non-call value operations are candidates for replacement. (We
        # could conceivably include calls to pure functions as values,
        # but determining purity would require an interprocedural
        # analysis.)
        computed_expr = None
        if instr.dest and instr.args and instr.op != 'call':
            # Construct a Expr for this computation.
            computed_expr = Expr(instr.op, argnums)

            # Is this value already available?
            idx = lookup_expr_num(expr2num, computed_expr)
            if idx is not None:
                # Mark this variable as containing the value.
                var2idx[instr.dest] = idx

                # Replace the instruction with a copy or a constant.
                if idx in num2const:  # Expr is a constant.
                    instr.mark_replace(bm.BrilInstruction_Const(dict(
                        op='const', dest=instr.dest, type=instr.type, value=num2const[idx]
                    )))
                else:  # Expr is in a variable.
                    instr.mark_replace(bm.BrilInstruction_Const(dict(
                        op='id', dest=instr.dest, type=instr.type, args=[expr_value_assigned_in_vars[idx][0]]
                    )))
                    expr_value_assigned_in_vars[idx].append(instr['dest'])  # new place holder for the expr value
                continue

        # If this instruction produces a result, give it a number.
        if instr.dest:
            new_block_idx = var2idx.assign(instr.dest)

            # Record constant values.
            if instr.op == 'const':
                num2const[new_block_idx] = instr.value

            if instr.is_last_assign_to_dest:
                # Preserve the variable name for other blocks.
                var = instr.dest
            else:
                # We must put the value in a new variable so it can be
                # reused by another computation in the feature (in case
                # the current variable name is reassigned before then).
                var = f'__{instr.dest}.lvn_{new_block_idx}'

            # Record the variable name and update the instruction.
            expr_value_assigned_in_vars[new_block_idx] = [var]
            instr.dest = var

            if computed_expr is not None:
                # Is this value foldable to a constant?
                const_equivilent = fold(num2const, computed_expr)
                if const_equivilent is not None:
                    num2const[new_block_idx] = const_equivilent
                    instr.mark_replace(bm.BrilInstruction_Const(dict(
                        op='const', dest=instr.dest, type=instr.type, value=const_equivilent
                    )))
                    continue

                # If not, record the new variable as the canonical
                # source for the newly computed value.
                expr2num[computed_expr] = new_block_idx







if __name__ == '__main__':
    # Parse the command-line argument.
    if len(sys.argv) == 1:
        pass
    else:
        raise ValueError("Usage: python3 lvn.py [] < input.bril.json > output.bril.json")

    # Read the input program, and create a BrilScript object.
    bril_in_dict = json.load(sys.stdin)
    bbs = bm.BrilScript(raw=bril_in_dict)

    for func in bbs.functions:
        for block in form_blocks(func.instrs):
            block_lvn_mark(block)
            # block[:] = [instr if instr.is_replaced == False else instr.is_replaced for instr in block]
        func.set_instrs([instr if instr.is_replaced == False else instr.is_replaced for instr in func.instrs])
    # print_blocks(bbs)  # for debugging
    
    # Output the modified program.
    json.dump(bbs.dump(), sys.stdout, indent=2, sort_keys=True)
