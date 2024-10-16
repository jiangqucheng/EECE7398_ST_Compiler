from typing import Set

BRIL_INSTR_ATTR_POS_SRC = ['pos', 'pos_end', 'src']
BRIL_OPCODE_CORE_ARITHMETIC = set(['add', 'mul', 'sub', 'div',])            # Bril:Core:Arithmetic
BRIL_OPCODE_CORE_COMPARISON = set(['eq', 'lt', 'gt', 'le', 'ge',])          # Bril:Core:Comparison
BRIL_OPCODE_CORE_LOGIC = set(['and', 'or', 'not',])                         # Bril:Core:Logic
BRIL_OPCODE_CORE_CONTROL = set(['jmp', 'br', 'call', 'ret',])               # Bril:Core:Control
BRIL_OPCODE_CORE_MISCELLANEOUS = set(['id', 'print', 'nop',])               # Bril:Core:Miscellaneous
BRIL_OPCODE_FLOAT_ARITHMETIC = set(['fadd', 'fmul', 'fsub', 'fdiv',])       # Bril:Float:Arithmetic
BRIL_OPCODE_FLOAT_COMPARISON = set(['feq', 'flt', 'fgt', 'fle', 'fge',])    # Bril:Float:Comparison
BRIL_OPCODE_ALL: Set[str] = \
    BRIL_OPCODE_CORE_ARITHMETIC | \
    BRIL_OPCODE_CORE_COMPARISON | \
    BRIL_OPCODE_CORE_LOGIC | \
    BRIL_OPCODE_FLOAT_ARITHMETIC | \
    BRIL_OPCODE_FLOAT_COMPARISON | \
    BRIL_OPCODE_CORE_CONTROL | \
    BRIL_OPCODE_CORE_MISCELLANEOUS
