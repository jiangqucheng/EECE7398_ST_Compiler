"""Create and print out the basic blocks in a Bril function.
"""

from typing import List, Iterator

from ._bril_struct import BrilScript, BrilInstruction, BrilInstruction_Label

# Instructions that terminate a basic block.
TERMINATORS = 'br', 'jmp', 'ret'


def form_blocks(instrs: List[BrilInstruction]) -> Iterator[List[BrilInstruction]]:
    """
    Forms basic blocks from a list of Bril instructions.

    A basic block is a sequence of instructions with no branches in except
    to the entry and no branches out except at the exit. This function
    yields lists of instructions, each representing a basic block.

    Args:
        instrs (List[BrilInstruction]): A list of Bril instructions.

    Yields:
        List[BrilInstruction]: A list of instructions representing a basic block.
    """
    # Start with an empty block.
    cur_block = []

    for instr in instrs:
        if instr.op:  # It's an instruction.
            # Add the instruction to the currently-being-formed block.
            cur_block.append(instr)

            # If this is a terminator (branching instruction), it's the
            # last instruction in the block. Finish this block and
            # start a new one.
            if instr.op in TERMINATORS:
                yield cur_block
                cur_block = []

        elif isinstance(instr, BrilInstruction_Label):  # It's a label.
            # End the block here (if it contains anything).
            if cur_block:
                yield cur_block

            # Start a new block with the label.
            cur_block = [instr]

    # Produce the final block, if any.
    if cur_block:
        yield cur_block


def print_blocks(bril: BrilScript):
    """
    Prints the basic blocks of each function in a given BrilScript.

    Args:
        bril (BrilScript): The BrilScript object containing functions to be processed.

    The function iterates over each function in the BrilScript, forms basic blocks from the instructions,
    and prints each block. If the block starts with a label, it prints the label; otherwise, it indicates
    that the block is anonymous. Each instruction within the block is printed with indentation for clarity.
    """
    for each_func in bril.functions:
        print(each_func)
        for block in form_blocks(each_func.instrs):
            # Mark the block.
            if isinstance(block[0], BrilInstruction_Label):
                print('block "{}":'.format(block[0].label))
                block = block[1:]  # Hide the label, for concision.
            else:
                print('anonymous block:')

            # Print the instructions.
            for instr in block:
                print(f'  {instr}')
        print()

