from __future__ import annotations
from typing import Any, Dict, List, Tuple, Union
from src.rpal_ast import ASTNode
from src.standardizer import standardize


class ControlInstruction:
    """
    Represents a single instruction for the CSE machine.
    For simplicity, store attributes like 'type' and 'value'.
    """

    def __init__(self, instr_type: str, value: Union[str, None] = None) -> None:
        self.instr_type: str = instr_type
        self.value: Union[str, None] = value

    def __repr__(self) -> str:
        return f"CI({self.instr_type!r}, {self.value!r})"


class Environment:
    """
    Represents an environment frame in the CSE machine.
    """

    def __init__(self, parent: Union[Environment, None] = None) -> None:
        self.bindings: Dict[str, Any] = {}
        self.parent: Union[Environment, None] = parent

    def lookup(self, name: str) -> Any:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.lookup(name)
        raise KeyError(f"Unbound variable '{name}'")

    def extend(self, name: str, value: Any) -> None:
        assert name not in self.bindings, f"Duplicate binding for '{name}'"
        self.bindings[name] = value


class CSEMachine:
    """
    Implements the Control‐Stack‐Environment machine for evaluating the ST.
    """

    def __init__(self) -> None:
        self.control: List[ControlInstruction] = []
        self.stack: List[Any] = []
        self.global_env = Environment()

    def generate_control(self, node: ASTNode) -> None:
        """
        Recursively traverse the ST to generate a flat list of ControlInstruction.
        """
        # Pseudocode: for each ASTNode, generate instructions depending on its label
        pass

    def run(self, std_root: ASTNode) -> Any:
        """
        Given a standardized tree, build the control list, initialize the environment/stack,
        then repeatedly apply rules until termination. Return the final value.
        """
        # 1. BUILD control list
        self.generate_control(std_root)
        # 2. Initialize stack with global environment, etc.
        # 3. While there are control instructions, apply next rule
        #    (pop control, inspect top of stack, depending on type, do appropriate operation)
        # 4. Return result at end
        pass


def get_result(source_code: str) -> Any:
    """
    Top‐level: take raw RPAL source, standardize into ST, then run CSEMachine on it.
    Returns either printed output or final value.
    """
    std_root = standardize(source_code)
    machine = CSEMachine()
    result = machine.run(std_root)
    return result
