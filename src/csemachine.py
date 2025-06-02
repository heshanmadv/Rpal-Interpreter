# src/csemachine.py

from __future__ import annotations
from typing import Any, Dict, List, Union
from src.standardizer import standardize
from src.rpal_ast import ASTNode


# ──────────────────────────────────────────────────────────────────────────────
# Stack implementation for the CSE machine
# ──────────────────────────────────────────────────────────────────────────────
class Stack:
    """
    A simple stack wrapper around a Python list, used as the operand stack in the CSE machine.
    """

    def __init__(self, name: str) -> None:
        self.name: str = name
        self._stack: List[Any] = []

    def push(self, item: Any) -> None:
        self._stack.append(item)

    def pop(self) -> Any:
        if not self._stack:
            raise IndexError(f"Pop from empty stack '{self.name}'")
        return self._stack.pop()

    def peek(self) -> Any:
        if not self._stack:
            raise IndexError(f"Peek from empty stack '{self.name}'")
        return self._stack[-1]

    def is_empty(self) -> bool:
        return len(self._stack) == 0

    def __len__(self) -> int:
        return len(self._stack)

    def __repr__(self) -> str:
        return f"{self.name}Stack({self._stack})"


# ──────────────────────────────────────────────────────────────────────────────
# Control-structure node classes (Lambda, Delta, Tau, Eta)
# ──────────────────────────────────────────────────────────────────────────────
class Lambda:
    """
    Represents a lambda instruction in the control structure.
    Fields:
      - number: unique index for this function
      - bounded_variable: comma-separated string of formal parameter names
      - environment: index of the environment in which this lambda was created
    """

    def __init__(self, number: int) -> None:
        self.number: int = number
        self.bounded_variable: str = ""  # e.g. "x" or "x,y,z"
        self.environment: int = 0        # environment index

    def __repr__(self) -> str:
        return f"Λ({self.number}, vars={self.bounded_variable}, env=e_{self.environment})"


class Delta:
    """
    Represents a delta (guard) instruction in the control structure.
    Fields:
      - number: unique index for this guard
    """

    def __init__(self, number: int) -> None:
        self.number: int = number

    def __repr__(self) -> str:
        return f"Δ({self.number})"


class Tau:
    """
    Represents a tuple-construction instruction in the control structure.
    Fields:
      - number: the arity of the tuple (how many elements to pop)
    """

    def __init__(self, number: int) -> None:
        self.number: int = number

    def __repr__(self) -> str:
        return f"τ({self.number})"


class Eta:
    """
    Represents an Eta (fixed-point) instruction in the control structure,
    used for Y*-recursion.
    Fields:
      - number: the index of the original lambda to re-create
      - bounded_variable: copied from the original Lambda
      - environment: copied from the original Lambda
    """

    def __init__(self, number: int) -> None:
        self.number: int = number
        self.bounded_variable: str = ""
        self.environment: int = 0

    def __repr__(self) -> str:
        return f"η({self.number}, vars={self.bounded_variable}, env=e_{self.environment})"


# ──────────────────────────────────────────────────────────────────────────────
# Environment class for the CSE machine
# ──────────────────────────────────────────────────────────────────────────────
class Environment:
    """
    Represents an environment frame in the CSE machine.
    Each environment has:
      - name (e.g., "e_0", "e_1", ...)
      - a dictionary of variable bindings
      - a reference to its parent environment
      - a list of child environments (used when exiting)
    """

    def __init__(self, name: str, parent: Union[Environment, None]) -> None:
        self.name: str = name
        self.bindings: Dict[str, Any] = {}
        self.parent: Union[Environment, None] = parent
        self.children: List[Environment] = []

    def lookup(self, var: str) -> Any:
        """
        Look up a variable in this environment or its ancestors.
        """
        if var in self.bindings:
            return self.bindings[var]
        if self.parent:
            return self.parent.lookup(var)
        raise KeyError(f"Unbound identifier '{var}'")

    def extend(self, var: str, value: Any) -> None:
        """
        Bind a new variable to this environment. Raises if already bound.
        """
        if var in self.bindings:
            raise AssertionError(
                f"Duplicate binding for '{var}' in environment {self.name}")
        self.bindings[var] = value

    def add_child(self, child: Environment) -> None:
        self.children.append(child)


# ──────────────────────────────────────────────────────────────────────────────
# The main CSEMachine class
# ──────────────────────────────────────────────────────────────────────────────
class CSEMachine:
    """
    Implements the Control-Stack-Environment (CSE) machine for evaluating a Standardized RPAL tree.
    """

    def __init__(self) -> None:
        # Each function or guard gets its own instruction list.
        self.control_structures: List[List[Union[str,
                                                 Lambda, Delta, Tau, Eta]]] = []
        # Counter to assign unique indices to Lambda and Delta nodes.
        self.count: int = 0

        # Dynamic control stack: holds instructions to be executed.
        self.control: List[Union[str, Lambda, Delta, Tau, Eta]] = []

        # Operand stack: holds runtime values, closures, environment markers, etc.
        self.stack: Stack = Stack("CSE")

        # List of active environments; index corresponds to environment number.
        self.environments: List[Environment] = []
        self.current_environment_index: int = 0

        # Create the global environment "e_0"
        global_env = Environment("e_0", None)
        self.environments.append(global_env)

        # Built-in function names recognized by the machine
        self.built_in_functions: List[str] = [
            "Order", "Print", "print", "Conc", "Stern", "Stem",
            "Isinteger", "Istruthvalue", "Isstring", "Istuple",
            "Isfunction", "ItoS"
        ]

        # Track if Print was invoked
        self.print_present: bool = False

    def generate_control(self, root: ASTNode, env_index: int) -> None:
        """
        Recursively traverse the standardized tree 'root' in post-order,
        appending instructions into self.control_structures[env_index].
        """
        # Ensure control_structures[env_index] exists
        while len(self.control_structures) <= env_index:
            self.control_structures.append([])

        instr_list = self.control_structures[env_index]
        val = root.value

        # CSE Rule 2: Lambda node → new function index
        if val == "lambda":
            self.count += 1
            func_index = self.count
            lam_instr = Lambda(func_index)

            # The first child of 'lambda' is the binding node: either ',' or a single <ID:x>
            bind_node = root.children[0]
            if bind_node.value == ",":
                # Multiple parameters
                names = [child.value[4:-1] for child in bind_node.children]
                lam_instr.bounded_variable = ",".join(names)
            else:
                # Single parameter
                lam_instr.bounded_variable = bind_node.value[4:-1]

            instr_list.append(lam_instr)
            # Recurse on the function body in the new function index
            self.generate_control(root.children[1], func_index)
            return

        # CSE Rule 8: Guard (->) node
        if val == "->":
            # Then-branch
            self.count += 1
            delta_then_index = self.count
            delta_then_instr = Delta(delta_then_index)
            instr_list.append(delta_then_instr)
            self.generate_control(root.children[1], delta_then_index)

            # Else-branch
            self.count += 1
            delta_else_index = self.count
            delta_else_instr = Delta(delta_else_index)
            instr_list.append(delta_else_instr)
            self.generate_control(root.children[2], delta_else_index)

            # "beta" to select based on condition
            instr_list.append("beta")
            # Condition itself is generated next in the current env
            self.generate_control(root.children[0], env_index)
            return

        # CSE Rule 9: Tuple formation (tau)
        if val == "tau":
            # Generate each element first
            for child in root.children:
                self.generate_control(child, env_index)
            # Now emit Tau(n)
            n = len(root.children)
            tau_instr = Tau(n)
            instr_list.append(tau_instr)
            return

        # Default: emit the node's value, then generate children
        instr_list.append(val)
        for child in root.children:
            self.generate_control(child, env_index)

    def run(self, std_root: ASTNode) -> Any:
        """
        Execute the CSE machine on the standardized tree 'std_root' and return the final result.
        Implements all CSE rules (1 through 13).
        """
        # 1. Build control structures for environment index 0 (main program)
        self.generate_control(std_root, 0)

        # 2. Initialize control & operand stack
        #    Push global environment marker "e_0"
        self.control.append(self.environments[0].name)
        self.control.extend(self.control_structures[0])
        self.stack.push(self.environments[0].name)

        # 3. Main CSE loop
        while self.control:
            instr = self.control.pop()

            # --- Rule 1: Literal or <ID:x> or <STR:...> or <true>/<false>/<nil> ---
            if isinstance(instr, str) and instr.startswith("<") and instr.endswith(">"):
                val = self._lookup(instr)
                self.stack.push(val)

            # --- Rule 2: Lambda => closure ---
            elif isinstance(instr, Lambda):
                clo = Lambda(instr.number)
                clo.bounded_variable = instr.bounded_variable
                clo.environment = self.current_environment_index
                self.stack.push(clo)

            # --- Rules 6 & 7: Primitive operators (binary/unary) ---
            elif instr in {"+", "-", "*", "/", "**", "gr", "ge", "ls", "le", "eq", "ne",
                           "or", "&", "aug", "neg", "not"}:
                self._apply_primitive(instr)

            # --- Rule 3: Application (gamma) ---
            elif instr == "gamma":
                rand = self.stack.pop()
                rator = self.stack.pop()

                # (4a) If rator is a Lambda closure → function call
                if isinstance(rator, Lambda):
                    func_idx = rator.number
                    bound_vars = rator.bounded_variable.split(",")
                    parent_env_idx = rator.environment

                    # Create new environment frame
                    new_env_idx = len(self.environments)
                    parent_env = self.environments[parent_env_idx]
                    new_env = Environment(f"e_{new_env_idx}", parent_env)
                    parent_env.add_child(new_env)
                    self.environments.append(new_env)

                    # Bind arguments
                    if len(bound_vars) > 1:
                        # rand should be a tuple
                        for i, var_name in enumerate(bound_vars):
                            new_env.extend(var_name, rand[i])
                    else:
                        new_env.extend(bound_vars[0], rand)

                    # Push new environment marker and then function instructions
                    self.stack.push(new_env.name)
                    self.control.append(new_env.name)
                    self.control.extend(self.control_structures[func_idx])

                # (4b) If rator is a tuple → tuple-selection (aug)
                elif isinstance(rator, tuple):
                    self.stack.push(rator[rand - 1])

                # (4c) If rator is "Y*" → Eta cell
                elif rator == "Y*":
                    eta_cell = Eta(rand.number)
                    eta_cell.bounded_variable = rand.bounded_variable
                    eta_cell.environment = rand.environment
                    self.stack.push(eta_cell)

                # (4d) If rator is an Eta cell → Y* recursion wiring
                elif isinstance(rator, Eta):
                    lam_cell = Lambda(rator.number)
                    lam_cell.bounded_variable = rator.bounded_variable
                    lam_cell.environment = rator.environment

                    # Push wiring: gamma gamma <rand> <Eta> <Lambda>
                    self.control.append("gamma")
                    self.control.append("gamma")
                    self.stack.push(rand)
                    self.stack.push(rator)
                    self.stack.push(lam_cell)

                # (4e) Otherwise, rator must be a built-in function name
                elif isinstance(rator, str) and rator in self.built_in_functions:
                    self._built_in(rator, rand)

                else:
                    raise RuntimeError(f"Unexpected rator in gamma: {rator}")

            # --- Rule 5: Exit environment (pop "e_N") ---
            elif isinstance(instr, str) and instr.startswith("e_"):
                saved_value = self.stack.pop()
                # Pop the environment marker from the stack
                self.stack.pop()
                # Restore previous environment index by scanning operand stack
                new_env_idx = 0
                for item in reversed(self.stack._stack):
                    if isinstance(item, str) and item.startswith("e_"):
                        new_env_idx = int(item[2:])
                        break
                self.current_environment_index = new_env_idx
                self.stack.push(saved_value)

            # --- Rule 9: Tuple formation (τ) ---
            elif isinstance(instr, Tau):
                n = instr.number
                elems: List[Any] = []
                for _ in range(n):
                    elems.append(self.stack.pop())
                tup = tuple(reversed(elems))
                self.stack.push(tup)

            # --- Rule 8: Conditional (delta + beta) ---
            elif instr == "beta":
                cond = self.stack.pop()
                else_delta = self.control.pop()
                then_delta = self.control.pop()
                if cond:
                    self.control.extend(
                        self.control_structures[then_delta.number])
                else:
                    self.control.extend(
                        self.control_structures[else_delta.number])

            else:
                raise RuntimeError(f"Unknown control instruction: {instr}")

        # 4. Once control is empty, the top of stack is the final result
        result = self.stack.pop()
        # Post-processing for printing/formatting
        return self._postprocess(result)

    def _lookup(self, token: str) -> Any:
        """
        Convert a token string to a Python value or environment lookup:
          - "<INT:5>"   → int(5)
          - "<STR:'hi'>"→ "hi"
          - "<ID:x>"    → lookup x in current environment (or built-in)
          - "<true>"    → True
          - "<false>"   → False
          - "<nil>"     → ()
          - "<dummy>"   → None
          - "Y*"        → "Y*"
        """
        inner = token[1:-1]
        parts = inner.split(":", 1)
        if len(parts) == 2:
            typ, val = parts
            if typ == "INT":
                return int(val)
            if typ == "STR":
                return val.strip("'")
            if typ == "ID":
                # Built-in function names are passed through
                if val in self.built_in_functions:
                    return val
                return self.environments[self.current_environment_index].lookup(val)
        else:
            if inner == "true":
                return True
            if inner == "false":
                return False
            if inner == "nil":
                return ()
            if inner == "dummy":
                return None
            if inner == "Y*":
                return "Y*"
        raise RuntimeError(f"Unrecognized token in lookup: {token}")

    def _built_in(self, function: str, argument: Any) -> None:
        """
        Handle built-in function calls: Order, Print, Conc, Stern, Stem, Isinteger, Istruthvalue, Isstring, Istuple, Isfunction, ItoS.
        Pushes result(s) onto self.stack and sets print_present if Print is called.
        """
        if function == "Order":
            self.stack.push(len(argument))

        elif function in ("Print", "print"):
            self.print_present = True
            if isinstance(argument, str):
                # Handle escape sequences
                argument = argument.replace("\\n", "\n").replace("\\t", "\t")
            print(argument)
            self.stack.push(argument)

        elif function == "Conc":
            s2 = self.stack.pop()
            result = argument + s2
            self.stack.push(result)

        elif function == "Stern":
            self.stack.push(argument[1:])

        elif function == "Stem":
            self.stack.push(argument[0])

        elif function == "Isinteger":
            self.stack.push(isinstance(argument, int))

        elif function == "Istruthvalue":
            self.stack.push(isinstance(argument, bool))

        elif function == "Isstring":
            self.stack.push(isinstance(argument, str))

        elif function == "Istuple":
            self.stack.push(isinstance(argument, tuple))

        elif function == "Isfunction":
            self.stack.push(argument in self.built_in_functions)

        elif function == "ItoS":
            if isinstance(argument, int):
                self.stack.push(str(argument))
            else:
                raise RuntimeError("ItoS expects an integer")

        else:
            raise RuntimeError(f"Unknown built-in function: {function}")

    def _apply_primitive(self, op: str) -> None:
        """
        Apply a primitive operator. Pops operands from the stack and pushes the result.
        Binary ops: +, -, *, /, **, gr, ge, ls, le, eq, ne, or, &, aug
        Unary ops: neg, not
        """
        # Binary operators
        if op in {"+", "-", "*", "/", "**", "gr", "ge", "ls", "le", "eq", "ne", "or", "&", "aug"}:
            b = self.stack.pop()
            a = self.stack.pop()
            if op == "+":
                self.stack.push(a + b)
            elif op == "-":
                self.stack.push(a - b)
            elif op == "*":
                self.stack.push(a * b)
            elif op == "/":
                # Integer division if both ints, else float
                if isinstance(a, int) and isinstance(b, int):
                    self.stack.push(a // b)
                else:
                    self.stack.push(a / b)
            elif op == "**":
                self.stack.push(a ** b)
            elif op == "gr":
                self.stack.push(a > b)
            elif op == "ge":
                self.stack.push(a >= b)
            elif op == "ls":
                self.stack.push(a < b)
            elif op == "le":
                self.stack.push(a <= b)
            elif op == "eq":
                self.stack.push(a == b)
            elif op == "ne":
                self.stack.push(a != b)
            elif op == "or":
                self.stack.push(a or b)
            elif op == "&":
                self.stack.push(a and b)
            elif op == "aug":
                # Original logic: if right-hand is a tuple, concatenate, else make tuple
                if isinstance(b, tuple):
                    self.stack.push(a + b)
                else:
                    self.stack.push(a + (b,))
            else:
                raise RuntimeError(f"Unknown binary operator: {op}")

        # Unary operators
        elif op == "neg":
            a = self.stack.pop()
            self.stack.push(-a)
        elif op == "not":
            a = self.stack.pop()
            self.stack.push(not a)
        else:
            raise RuntimeError(f"Unknown unary operator: {op}")

    def _postprocess(self, result: Any) -> Any:
        """
        Final formatting:
          - boolean True/False → "true"/"false"
          - tuples → "(x, y, ...)" or "(x)" if singleton
        """
        if isinstance(result, bool):
            return str(result).lower()

        if isinstance(result, tuple):
            processed: List[Any] = []
            for elem in result:
                if isinstance(elem, bool):
                    processed.append(str(elem).lower())
                else:
                    processed.append(elem)
            if len(processed) == 1:
                return f"({processed[0]})"
            inside = ", ".join(str(e) for e in processed)
            return f"({inside})"

        return result


def get_result(source_code: str) -> Any:
    """
    Top-level: take raw RPAL source, standardize into ST, then run CSEMachine.
    Prints the result if Print was used; otherwise returns the final value.
    """
    machine = CSEMachine()
    std_root = standardize(source_code)
    result = machine.run(std_root)
    if not machine.print_present:
        print(result)
    return result
