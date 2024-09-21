import json
import sys

def is_add_or_fadd(op):
    """
    Check if the given operation is 'add' or 'fadd'.

    Parameters:
    op (str): The operation to check.

    Returns:
    bool: True if the operation is 'add' or 'fadd', False otherwise.
    """
    return op in ["add", "fadd"]

def add_print_after_add_or_fadd(bril):
    """
    Adds a print instruction after each add or fadd instruction in the given Bril program.

    Args:
        bril (dict): The Bril program represented as a dictionary.

    Returns:
        dict: The modified Bril program with print instructions added.

    Example:
        >>> bril = {
        ...     'functions': [
        ...         {
        ...             'name': 'main',
        ...             'instrs': [
        ...                 {'op': 'const', 'dest': 'x', 'type': 'int', 'value': 1},
        ...                 {'op': 'const', 'dest': 'y', 'type': 'int', 'value': 2},
        ...                 {'op': 'add', 'dest': 'z', 'type': 'int', 'args': ['x', 'y']},
        ...             ]
        ...         }
        ...     ]
        ... }
        >>> add_print_after_add_or_fadd(bril)
        {
            'functions': [
                {
                    'name': 'main',
                    'instrs': [
                        {'op': 'const', 'dest': 'x', 'type': 'int', 'value': 1},
                        {'op': 'const', 'dest': 'y', 'type': 'int', 'value': 2},
                        {'op': 'add', 'dest': 'z', 'type': 'int', 'args': ['x', 'y']},
                        {'op': 'print', 'args': ['x', 'y', 'z']}
                    ]
                }
            ]
        }
    """
    for func in bril['functions']:
        new_instrs = []
        for instr in func['instrs']:
            new_instrs.append(instr)
            if 'op' in instr and is_add_or_fadd(instr['op']):
                print_instr = dict(op="print", args=[*instr['args'], instr['dest']])
                new_instrs.append(print_instr)
                print(f"Added print instruction after {instr}.", file=sys.stderr)
        func['instrs'] = new_instrs
    return bril

def main():
    """
    Main function that reads a Bril program from an input file, adds print statements after each add or fadd instruction,
    and writes the modified Bril program to the standard output.

    Args:
        None

    Returns:
        None
    """
    if len(sys.argv) != 2:
        print("Usage: python pin_stub_print_add.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    with open(input_file, 'r') as f:
        bril = json.load(f)

    bril = add_print_after_add_or_fadd(bril)

    json.dump(bril, sys.stdout, indent=2)

if __name__ == "__main__":
    main()