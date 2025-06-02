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
class Environment():
    """
    Represents an environment in the CSE machine, which holds variables and child environments.
    Fields:
      - name: unique identifier for the environment (e.g., "e_0", "e_1", ...)
      - variables: dictionary of variable names and their values
      - children: list of child environments
      - parent: reference to the parent environment
    """

    def __init__(self, number, parent):
        self.name = "e_" + str(number)
        self.variables = {}
        self.children = []
        self.parent = parent

    # This function adds a child to the current environment.
    def add_child(self, child):
        self.children.append(child)
        child.variables.update(self.variables)

    # This function adds a variable to the current environment.
    def add_variable(self, key, value):
        self.variables[key] = value


# ──────────────────────────────────────────────────────────────────────────────
# The main CSEMachine class
# ──────────────────────────────────────────────────────────────────────────────
class CSEMachine:
    def __init__(self):
        self.control_structures = []
        self.count = 0
        self.control = []
        # Stack for the CSE machine
        self.stack = Stack("CSE")
        self.environments = [Environment(0, None)]
        self.current_environment = 0
        self.builtInFunctions = [
            "Order", "Print", "print", "Conc", "Stern", "Stem",
            "Isinteger", "Istruthvalue", "Isstring", "Istuple",
            "Isfunction", "ItoS"
        ]
        self.print_present = False

    def generate_control_structure(self, root, i):
        # Ensure there's a list at index i
        while len(self.control_structures) <= i:
            self.control_structures.append([])

        if root.value == "lambda":
            self.count += 1
            left_child = root.children[0]
            temp = Lambda(self.count)
            if left_child.value == ",":
                vars_concat = ",".join(
                    child.value[4:-1] for child in left_child.children)
                temp.bounded_variable = vars_concat
            else:
                temp.bounded_variable = left_child.value[4:-1]
            self.control_structures[i].append(temp)
            for child in root.children[1:]:
                self.generate_control_structure(child, self.count)

        elif root.value == "->":
            # Delta for then-branch
            self.count += 1
            temp_then = Delta(self.count)
            self.control_structures[i].append(temp_then)
            self.generate_control_structure(root.children[1], self.count)
            # Delta for else-branch
            self.count += 1
            temp_else = Delta(self.count)
            self.control_structures[i].append(temp_else)
            self.generate_control_structure(root.children[2], self.count)
            # Beta node
            self.control_structures[i].append("beta")
            # Condition expression
            self.generate_control_structure(root.children[0], i)

        elif root.value == "tau":
            n = len(root.children)
            temp = Tau(n)
            self.control_structures[i].append(temp)
            for child in root.children:
                self.generate_control_structure(child, i)

        else:
            self.control_structures[i].append(root.value)
            for child in root.children:
                self.generate_control_structure(child, i)

    def lookup(self, name):
        # Handles tokens of form '<TYPE:value>' or '<value>'
        inner = name[1:-1]
        parts = inner.split(":")
        if len(parts) == 1:
            value = parts[0]
        else:
            data_type, value = parts[0], parts[1]
            if data_type == "INT":
                return int(value)
            elif data_type == "STR":
                return value.strip("'")
            elif data_type == "ID":
                if value in self.builtInFunctions:
                    return value
                else:
                    try:
                        return self.environments[self.current_environment].variables[value]
                    except KeyError:
                        print(f"Undeclared Identifier: {value}")
                        exit(1)

        if value == "Y*":
            return "Y*"
        elif value == "nil":
            return ()
        elif value == "true":
            return True
        elif value == "false":
            return False

    def built_in(self, function, argument):
        # The Order function returns the length of a tuple.
        if function == "Order":
            order = len(argument)
            self.stack.push(order)

        # The Print function prints the output to the command prompt.
        elif function in ("Print", "print"):
            self.print_present = True
            if isinstance(argument, str):
                argument = argument.replace("\\n", "\n").replace("\\t", "\t")
            self.stack.push(argument)

        # The Conc function concatenates two strings.
        elif function == "Conc":
            second = self.stack.pop()
            self.control.pop()
            concatenated = argument + second
            self.stack.push(concatenated)

        # The Stern function returns the string without the first letter.
        elif function == "Stern":
            self.stack.push(argument[1:])

        # The Stem function returns the first letter of the given string.
        elif function == "Stem":
            self.stack.push(argument[0])

        # The Isinteger function checks if the given argument is an integer.
        elif function == "Isinteger":
            self.stack.push(isinstance(argument, int))

        # The Istruthvalue function checks if the given argument is a boolean.
        elif function == "Istruthvalue":
            self.stack.push(isinstance(argument, bool))

        # The Isstring function checks if the given argument is a string.
        elif function == "Isstring":
            self.stack.push(isinstance(argument, str))

        # The Istuple function checks if the given argument is a tuple.
        elif function == "Istuple":
            self.stack.push(isinstance(argument, tuple))

        # The Isfunction function checks if the given argument is a built-in function.
        elif function == "Isfunction":
            self.stack.push(argument in self.builtInFunctions)

        # The ItoS function converts integers to strings.
        elif function == "ItoS":
            if isinstance(argument, int):
                self.stack.push(str(argument))
            else:
                print("Error: ItoS function can only accept integers.")
                exit(1)

    def apply_rules(self):
        op = ["+", "-", "*", "/", "**", "gr", "ge",
              "ls", "le", "eq", "ne", "or", "&", "aug"]
        uop = ["neg", "not"]

        while self.control:
            symbol = self.control.pop()

            # Rule 1: literal or identifier
            if isinstance(symbol, str) and symbol.startswith("<") and symbol.endswith(">"):
                self.stack.push(self.lookup(symbol))

            # Rule 2: lambda
            elif isinstance(symbol, Lambda):
                temp = Lambda(symbol.number)
                temp.bounded_variable = symbol.bounded_variable
                temp.environment = self.current_environment
                self.stack.push(temp)

            # Rule 4: gamma (application)
            elif symbol == "gamma":
                arg = self.stack.pop()
                fun = self.stack.pop()

                # Lambda application
                if isinstance(arg, Lambda):
                    self.current_environment = len(self.environments)
                    lambda_number = arg.number
                    bounded_variable = arg.bounded_variable
                    parent_env_number = arg.environment

                    parent_env = self.environments[parent_env_number]
                    child_env = Environment(
                        self.current_environment, parent_env)
                    parent_env.add_child(child_env)
                    self.environments.append(child_env)

                    vars_list = bounded_variable.split(",")
                    if len(vars_list) > 1:
                        for idx, var in enumerate(vars_list):
                            child_env.add_variable(var, fun[idx])
                    else:
                        child_env.add_variable(bounded_variable, fun)

                    self.stack.push(child_env.name)
                    self.control.append(child_env.name)
                    self.control.extend(self.control_structures[lambda_number])

                # Tuple indexing
                elif isinstance(arg, tuple):
                    self.stack.push(arg[fun - 1])

                # Eta expansion
                elif arg == "Y*":
                    temp_eta = Eta(fun.number)
                    temp_eta.bounded_variable = fun.bounded_variable
                    temp_eta.environment = fun.environment
                    self.stack.push(temp_eta)

                elif isinstance(arg, Eta):
                    temp_lambda = Lambda(arg.number)
                    temp_lambda.bounded_variable = arg.bounded_variable
                    temp_lambda.environment = arg.environment
                    self.control.append("gamma")
                    self.control.append("gamma")
                    self.stack.push(fun)
                    self.stack.push(arg)
                    self.stack.push(temp_lambda)

                # Built-in functions
                elif arg in self.builtInFunctions:
                    self.built_in(arg, fun)

            # Rule 5: environment marker
            elif isinstance(symbol, str) and symbol.startswith("e_"):
                value = self.stack.pop()
                self.stack.pop()
                if self.current_environment != 0:
                    for element in reversed(self.stack):
                        if isinstance(element, str) and element.startswith("e_"):
                            self.current_environment = int(element[2:])
                            break
                self.stack.push(value)

            # Rule 6: binary operators
            elif symbol in op:
                rhs = self.stack.pop()
                lhs = self.stack.pop()
                if symbol == "+":
                    self.stack.push(lhs + rhs)
                elif symbol == "-":
                    self.stack.push(lhs - rhs)
                elif symbol == "*":
                    self.stack.push(lhs * rhs)
                elif symbol == "/":
                    self.stack.push(lhs // rhs)
                elif symbol == "**":
                    self.stack.push(lhs ** rhs)
                elif symbol == "gr":
                    self.stack.push(lhs > rhs)
                elif symbol == "ge":
                    self.stack.push(lhs >= rhs)
                elif symbol == "ls":
                    self.stack.push(lhs < rhs)
                elif symbol == "le":
                    self.stack.push(lhs <= rhs)
                elif symbol == "eq":
                    self.stack.push(lhs == rhs)
                elif symbol == "ne":
                    self.stack.push(lhs != rhs)
                elif symbol == "or":
                    self.stack.push(lhs or rhs)
                elif symbol == "&":
                    self.stack.push(lhs and rhs)
                elif symbol == "aug":
                    if isinstance(rhs, tuple):
                        self.stack.push(lhs + rhs)
                    else:
                        self.stack.push(lhs + (rhs,))

            # Rule 7: unary operators
            elif symbol in uop:
                operand = self.stack.pop()
                if symbol == "not":
                    self.stack.push(not operand)
                elif symbol == "neg":
                    self.stack.push(-operand)

            # Rule 8: beta (conditional)
            elif symbol == "beta":
                B = self.stack.pop()
                else_part = self.control.pop()
                then_part = self.control.pop()
                if B:
                    self.control.extend(
                        self.control_structures[then_part.number])
                else:
                    self.control.extend(
                        self.control_structures[else_part.number])

            # Rule 9: tau (tuple construction)
            elif isinstance(symbol, Tau):
                n = symbol.number
                items = [self.stack.pop() for _ in range(n)]
                self.stack.push(tuple(items))

            # Rule 10 & 11 & 12 & 13: handled within Rule 4

            # Rule: Y* propagates as is
            elif symbol == "Y*":
                self.stack.push(symbol)

        # Post-processing: convert lambda to closure string
        if isinstance(self.stack[0], Lambda):
            lam = self.stack[0]
            self.stack[0] = f"[lambda closure: {lam.bounded_variable}: {lam.number}]"

        # Post-processing: tuple and boolean formatting
        top = self.stack[0]
        if isinstance(top, tuple):
            converted = list(top)
            for idx, elem in enumerate(converted):
                if isinstance(elem, bool):
                    converted[idx] = str(elem).lower()
            if len(converted) == 1:
                self.stack[0] = f"({converted[0]})"
            else:
                if any(isinstance(el, str) for el in converted):
                    joined = ", ".join(str(el) for el in converted)
                    self.stack[0] = f"({joined})"
                else:
                    self.stack[0] = tuple(converted)

        if self.stack[0] is True or self.stack[0] is False:
            self.stack[0] = str(self.stack[0]).lower()

    def interpret(self, file_name):
        st = standardize(file_name)
        self.generate_control_structure(st, 0)

        # Bootstrap the control list
        root_env_name = self.environments[0].name
        self.control.append(root_env_name)
        self.control.extend(self.control_structures[0])
        self.stack.push(root_env_name)

        self.apply_rules()

        if self.print_present:
            print(self.stack[0])


def get_result(file_name):
    csemachine = CSEMachine()
    csemachine.interpret(file_name)
