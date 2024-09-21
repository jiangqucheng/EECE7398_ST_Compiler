import json
import sys

def is_branch_or_jump(op):
    """
    Check if the given operation is a branch or jump instruction.

    Parameters:
        op (str): The operation to check.

    Returns:
        bool: True if the operation is a branch or jump instruction, False otherwise.
    """
    return op in ["jmp", "br"]

def add_print_before_branch_or_jump(bril):
    """
    Adds a print instruction before each branch or jump instruction in the given Bril program.

    Args:
        bril (dict): The Bril program represented as a dictionary.

    Returns:
        dict: The modified Bril program with print instructions added before branch or jump instructions.
    """
    for func in bril['functions']:
        new_instrs = []
        for instr in func['instrs']:
            if 'op' in instr and is_branch_or_jump(instr['op']):
                print_instr = dict(op="print", args=[])
                # Collect arguments from the previous instruction if available
                if len(new_instrs): print_instr["args"] = [new_instrs[-1]['dest' if 'dest' in new_instrs[-1] else 'args']]
                new_instrs.append(print_instr)
                print(f"Added print instruction before {instr}.", file=sys.stderr)
            new_instrs.append(instr)
        func['instrs'] = new_instrs
    return bril

def main():
    """
    Main function that reads a Bril program from an input file, adds print statements before branch or jump instructions,
    and dumps the modified Bril program to the standard output.

    Args:
        None

    Returns:
        None
    """
    if len(sys.argv) != 2:
        print("Usage: python pin_stub_print_jmp.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    with open(input_file, 'r') as f:
        bril = json.load(f)

    bril = add_print_before_branch_or_jump(bril)

    json.dump(bril, sys.stdout, indent=2)

if __name__ == "__main__":
    main()