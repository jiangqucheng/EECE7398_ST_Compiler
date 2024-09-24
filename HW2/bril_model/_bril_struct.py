import os, sys
from copy import deepcopy
from typing import List, Dict, Union
from ._bril_loader import load_bril
from ._bril_constant import BRIL_INSTR_ATTR_POS_SRC, BRIL_OPCODE_ALL


class BrilInstruction():
    def __init__(self, raw: dict):
        self._raw = deepcopy(raw)
        # raise error if there are any other keys.
        AVAILABLE_KEYS = set(['dest', 'type', 'op', 'args', 'funcs', 'labels', 'value', 'label'] + BRIL_INSTR_ATTR_POS_SRC)
        _unparsed_keys = set(raw.keys()) - AVAILABLE_KEYS
        if _unparsed_keys: raise NotImplementedError(f"{self.__class__.__name__}::Unrecognized keys: {_unparsed_keys} in {raw}")

    @property
    def dest(self) -> str:
        return self._raw['dest'] if 'dest' in self._raw else None
    @property
    def type(self) -> str:
        return self._raw['type'] if 'type' in self._raw else None
    @property
    def op(self) -> str:
        return self._raw['op'] if 'op' in self._raw else None
    @property
    def args(self) -> List[str]:
        return self._raw['args'] if 'args' in self._raw else None
    @property
    def funcs(self) -> List[str]:
        return self._raw['funcs'] if 'funcs' in self._raw else None
    @property
    def labels(self) -> List[str]:
        return self._raw['labels'] if 'labels' in self._raw else None
    @property
    def value(self) -> int:
        return self._raw['value'] if 'value' in self._raw else None
    @property
    def label(self) -> str:
        return self._raw['label'] if 'label' in self._raw else None
    @property
    def pos(self) -> Dict[str, int]:
        return self._raw['pos'] if 'pos' in self._raw else None
    @property
    def pos_end(self) -> Dict[str, int]:
        return self._raw['pos_end'] if 'pos_end' in self._raw else None
    @property
    def src(self) -> str:
        return self._raw['src'] if 'src' in self._raw else None

    def __repr__(self):
        if self.label:
            return f"{self.__class__.__name__} ::\t[{self.label}]"
        _args = ', '.join(self.args) if self.args else self.value
        _args = ', '.join(self.funcs) if self.funcs else _args
        _args = ', '.join(self.labels) if self.labels else _args
        _dest = f"{self.dest if self.dest else ''}" + " " + (f"({self.type})" if self.type else '') + " <- "
        _dest = '' if (not self.dest) and (not self.type) else _dest
        return f"{self.__class__.__name__} ::\t{_dest}[{self.op}] {_args}"
    def dump(self) -> dict:
        return self._raw

class BrilInstruction_Const(BrilInstruction):
    def __init__(self, raw: dict):
        super().__init__(raw)
        if self.op != 'const':
            raise TypeError(f"{self.__class__.__name__}::Unrecognized op: {self.op} in {self._raw}")
        # raise error if there are any other keys.
        AVAILABLE_KEYS = set(['dest', 'type', 'op', 'value'] + BRIL_INSTR_ATTR_POS_SRC)
        _unparsed_keys = set(raw.keys()) - AVAILABLE_KEYS
        if _unparsed_keys: raise NotImplementedError(f"{self.__class__.__name__}::Unrecognized keys: {_unparsed_keys} in {raw}")

    @property
    def value(self) -> Union[int, bool]:
        return self._raw['value']
    @property
    def dest(self) -> str:
        return self._raw['dest']
    @property
    def type(self) -> str:
        return self._raw['type']

    def __repr__(self):
        return f"{self.__class__.__name__} ::\t{self.dest} ({self.type}) <- [{self.op}] {self.value}"

class BrilInstruction_Label(BrilInstruction):
    def __init__(self, raw: dict):
        super().__init__(raw)
        if self.label is None:
            raise TypeError(f"{self.__class__.__name__}::label must be provided in {self._raw}")
        # raise error if there are any other keys.
        AVAILABLE_KEYS = set(['label'] + BRIL_INSTR_ATTR_POS_SRC)
        _unparsed_keys = set(raw.keys()) - AVAILABLE_KEYS
        if _unparsed_keys: raise NotImplementedError(f"{self.__class__.__name__}::Unrecognized keys: {_unparsed_keys} in {raw}")

    @property
    def label(self) -> str:
        return self._raw['label']
    
    def __repr__(self):
        return f"{self.__class__.__name__} ::\t<|.{self.label}|>"

class BrilInstruction_ValOp(BrilInstruction):
    def __init__(self, raw: dict):
        super().__init__(raw)
        if self.op not in BRIL_OPCODE_ALL:
            raise TypeError(f"{self.__class__.__name__}::Unrecognized op: {self.op} in {self._raw}")
        if 'dest' not in self._raw or 'type' not in self._raw :
            raise TypeError(f"{self.__class__.__name__}::dest and type must be provided in {self._raw}")
        if 'args' not in self._raw and 'funcs' not in self._raw and 'labels' not in self._raw :
            raise TypeError(f"{self.__class__.__name__}::one of [args/funcs/labels] must be provided in {self._raw}")
        # raise error if there are any other keys.
        AVAILABLE_KEYS = set(['dest', 'type', 'op', 'args', 'funcs', 'labels'] + BRIL_INSTR_ATTR_POS_SRC)
        _unparsed_keys = set(raw.keys()) - AVAILABLE_KEYS
        if _unparsed_keys: raise NotImplementedError(f"{self.__class__.__name__}::Unrecognized keys: {_unparsed_keys} in {raw}")
    
    @property
    def op(self) -> str:
        return self._raw['op']
    @property
    def dest(self) -> str:
        return self._raw['dest']
    @property
    def type(self) -> str:
        return self._raw['type']
    @property
    def args(self) -> List[str]:
        return self._raw['args'] if 'args' in self._raw else None
    @property
    def funcs(self) -> List[str]:
        return self._raw['funcs'] if 'funcs' in self._raw else None
    @property
    def labels(self) -> List[str]:
        return self._raw['labels'] if 'labels' in self._raw else None
    
    def __repr__(self):
        _args = ', '.join(self.args) if self.args else ''
        _args = ', '.join(self.funcs) if self.funcs else _args
        _args = ', '.join(self.labels) if self.labels else _args
        _dest = f"{self.dest if self.dest else ''}" + " " + (f"({self.type})" if self.type else '') + " <- "
        _dest = '' if (not self.dest) and (not self.type) else _dest
        return f"{self.__class__.__name__} ::\t{_dest}[{self.op}] {_args}"

class BrilInstruction_EffOp(BrilInstruction):
    def __init__(self, raw: dict):
        super().__init__(raw)
        if self.op not in BRIL_OPCODE_ALL:
            raise TypeError(f"{self.__class__.__name__}::Unrecognized op: {self.op} in {self._raw}")
        if 'dest' in self._raw or 'type' in self._raw :
            raise TypeError(f"{self.__class__.__name__}::dest and type must be provided in {self._raw}")
        if 'args' not in self._raw and 'funcs' not in self._raw and 'labels' not in self._raw and self.op != 'ret':
            raise TypeError(f"{self.__class__.__name__}::one of [args/funcs/labels] must be provided in {self._raw}")
        # raise error if there are any other keys.
        AVAILABLE_KEYS = set(['dest', 'type', 'op', 'args', 'funcs', 'labels'] + BRIL_INSTR_ATTR_POS_SRC)
        _unparsed_keys = set(raw.keys()) - AVAILABLE_KEYS
        if _unparsed_keys: raise NotImplementedError(f"{self.__class__.__name__}::Unrecognized keys: {_unparsed_keys} in {raw}")
    
    @property
    def op(self) -> str:
        return self._raw['op']
    @property
    def args(self) -> List[str]:
        return self._raw['args'] if 'args' in self._raw else None
    @property
    def funcs(self) -> List[str]:
        return self._raw['funcs'] if 'funcs' in self._raw else None
    @property
    def labels(self) -> List[str]:
        return self._raw['labels'] if 'labels' in self._raw else None
    
    def __repr__(self):
        _args = ', '.join(self.args) if self.args else ''
        _args = ', '.join(self.funcs) if self.funcs else _args
        _args = ', '.join(self.labels) if self.labels else _args
        return f"{self.__class__.__name__} ::\t[{self.op}] {_args}"

class BrilFunction():
    def __init__(self, raw: dict):
        self._instrs = []
        for instr in raw['instrs']:
            try:
                if 'label' in instr:
                    self._instrs.append(BrilInstruction_Label(instr))
                elif 'op' in instr and instr['op'] == 'const':
                    self._instrs.append(BrilInstruction_Const(instr))
                else:
                    self._instrs.append(BrilInstruction_ValOp(instr))
            except TypeError:
                try:
                    self._instrs.append(BrilInstruction_EffOp(instr))
                except TypeError:
                    self._instrs.append(BrilInstruction(instr))
                    print(f"Warning: Unrecognized instruction: {instr}", file=sys.stderr)
        raw.pop('instrs', None)
        self._raw = deepcopy(raw)
        # raise error if there are any other keys.
        AVAILABLE_KEYS = set(['name', 'type', 'args'] + BRIL_INSTR_ATTR_POS_SRC)
        _unparsed_keys = set(raw.keys()) - AVAILABLE_KEYS
        if _unparsed_keys: raise NotImplementedError(f"{self.__class__.__name__}::Unrecognized keys: {_unparsed_keys} in {raw}")

    @property
    def name(self) -> str:
        return self._raw['name'] if 'name' in self._raw else None
    @property
    def type(self) -> str:
        return self._raw['type'] if 'type' in self._raw else None
    @property
    def args(self) -> List[Dict[str, str]]:
        return self._raw['args'] if 'args' in self._raw else None
    @property
    def pos(self) -> Dict[str, int]:
        return self._raw['pos'] if 'pos' in self._raw else None
    @property
    def instrs(self) -> List[BrilInstruction]:
        return self._instrs

    def __repr__(self):
        arg_dict2str = lambda each_arg_dict: f"{each_arg_dict['name'] if 'name' in each_arg_dict else ''}" + (f"<{each_arg_dict['type']}>" if 'type' in each_arg_dict else '')
        _args = ', '.join([arg_dict2str(x) for x in self.args]) if self.args else ''
        return f"{self.__class__.__name__} ::\t{self.name} ( {_args} ) -> {self.type}: <{len(self.instrs)} instr>"
    def dump(self) -> dict:
        ret_dict = deepcopy(self._raw)
        ret_dict['instrs'] = [instr.dump() for instr in self.instrs]
        return ret_dict

class BrilScript():
    def __init__(self, *, raw: dict = None, script_name: str = '<Anonymous>', file_dir: str = ''):
        self.script_name = script_name
        self.file_dir = file_dir
        if raw is None:
            raw = load_bril(os.path.join(file_dir, script_name), include_pos=True)
        self._funcs = [BrilFunction(func) for func in raw['functions']]
        raw.pop('functions', None)
        self._raw = deepcopy(raw)
        # raise error if there are any other keys.
        AVAILABLE_KEYS = set([] + BRIL_INSTR_ATTR_POS_SRC)
        _unparsed_keys = set(raw.keys()) - AVAILABLE_KEYS
        if _unparsed_keys: raise NotImplementedError(f"{self.__class__.__name__}::Unrecognized keys: {_unparsed_keys} in {raw}")

    @property
    def functions(self) -> list[BrilFunction]:
        return self._funcs

    def __repr__(self):
        _at_dir = f" @ {self.file_dir}" if self.file_dir else ''
        return f"{self.__class__.__name__} ::\t{self.script_name} <{len(self._funcs)} func>{_at_dir}"
    def dump(self) -> dict:
        ret_dict = deepcopy(self._raw)
        ret_dict['functions'] = [instr.dump() for instr in self.functions]
        return ret_dict

    def show(self):
        print(self)
        print()
        for func in self.functions:
            print(func)
            for instr in func.instrs:
                print(f"  {instr}")
            print()
