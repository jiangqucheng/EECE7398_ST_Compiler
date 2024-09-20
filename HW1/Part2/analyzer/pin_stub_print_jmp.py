import json
import sys

def is_branch_or_jump(op):
    return op in ["jmp", "br"]

def add_print_before_branch_or_jump(bril):
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