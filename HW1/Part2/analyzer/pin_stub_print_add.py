import json
import sys

def is_add_or_fadd(op):
    return op in ["add", "fadd"]

def add_print_after_add_or_fadd(bril):
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