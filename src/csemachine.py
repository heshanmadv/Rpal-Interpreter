from src.standardizer import standardize
from src.node import *
from src.environment import Environment
from src.stack import Stack
from src.structures import *

control_structures = []
count = 0
control = []
stack = Stack("CSE")                        # Stack for the CSE machine
environments = [Environment(0, None)]
current_environment = 0
builtInFunctions = ["Order", "Print", "print", "Conc", "Stern", "Stem", "Isinteger", "Istruthvalue", "Isstring", "Istuple", "Isfunction", "ItoS"]
print_present = False


def generate_control_structure(root, i):
    global count
    
    while(len(control_structures) <= i):
        control_structures.append([])

    # When lambda is encountered, we have to generate a new control structure.
    if (root.value == "lambda"):
        count += 1
        left_child = root.children[0]
        if (left_child.value == ","):
            temp = Lambda(count)
            
            x = ""
            for child in left_child.children:
                x += child.value[4:-1] + ","
            x = x[:-1]
            
            temp.bounded_variable = x
            control_structures[i].append(temp)
        else:
            temp = Lambda(count)
            temp.bounded_variable = left_child.value[4:-1]
            control_structures[i].append(temp)

        for child in root.children[1:]:
            generate_control_structure(child, count)

    elif (root.value == "->"):
        count += 1
        temp = Delta(count)
        control_structures[i].append(temp)
        generate_control_structure(root.children[1], count)
        count += 1
        temp = Delta(count)
        control_structures[i].append(temp)
        generate_control_structure(root.children[2], count)
        control_structures[i].append("beta")
        generate_control_structure(root.children[0], i)

    elif (root.value == "tau"):
        n = len(root.children)
        temp = Tau(n)
        control_structures[i].append(temp)
        for child in root.children:
            generate_control_structure(child, i)

    else:
        control_structures[i].append(root.value)
        for child in root.children:
            generate_control_structure(child, i)

# This function is used for tokens that begin with '<' and end with '>'.
def lookup(name):
    name = name[1:-1]
    info = name.split(":")
    
    if (len(info) == 1):
        value = info[0]
    else:
        data_type = info[0]
        value = info[1]
    
        if data_type == "INT":
            return int(value)
        
        # The rpal.exe program detects srings only when they begin with ' and end with '.
        # Our code must emulate this behaviour.
        elif data_type == "STR":
            return value.strip("'")
        elif data_type == "ID":
            if (value in builtInFunctions):
                return value
            else:
                try:
                    value = environments[current_environment].variables[value]
                except KeyError:
                    print("Undeclared Identifier: " + value)
                    exit(1)
                else:
                    return value
            
    if value == "Y*":
        return "Y*"
    elif value == "nil":
        return ()
    elif value == "true":
        return True
    elif value == "false":
        return False
    
def built_in(function, argument):
    global print_present
    
    # The Order function returns the length of a tuple.  
    if (function == "Order"):
        order = len(argument)
        stack.push(order)

    # The Print function prints the output to the command prompt.
    elif (function == "Print" or function == "print"):
        # We should print the output only when the 'Print' function is called in the program.
        print_present = True
        
        # If there are escape characters in the string, we need to format it properly.
        if type(argument) == str:
            if "\\n" in argument:
                argument = argument.replace("\\n", "\n")
            if "\\t" in argument:
                argument = argument.replace("\\t", "\t")

        stack.push(argument)

    # The Conc function concatenates two strings.
    elif (function == "Conc"):
        stack_symbol = stack.pop()
        control.pop()
        temp = argument + stack_symbol
        stack.push(temp)

    # The Stern function returns the string without the first letter.
    elif (function == "Stern"):
        stack.push(argument[1:])

    # The Stem function returns the first letter of the given string.
    elif (function == "Stem"):
        stack.push(argument[0])

    # The Isinteger function checks if the given argument is an integer.
    elif (function == "Isinteger"):
        if (type(argument) == int):
            stack.push(True)
        else:
            stack.push(False)

    # The Istruthvalue function checks if the given argument is a boolean value.               
    elif (function == "Istruthvalue"):
        if (type(argument) == bool):
            stack.push(True)
        else:
            stack.push(False)

    # The Isstring function checks if the given argument is a string.
    elif (function == "Isstring"):
        if (type(argument) == str):
            stack.push(True)
        else:
            stack.push(False)

    # The Istuple function checks if the given argument is a tuple.
    elif (function == "Istuple"):
        if (type(argument) == tuple):
            stack.push(True)
        else:
            stack.push(False)

    # The Isfunction function checks if the given argument is a built-in function.
    elif (function == "Isfunction"):
        if (argument in builtInFunctions):
            return True
        else:
            False
    
    # The ItoS function converts integers to strings.        
    elif (function == "ItoS"):
        if (type(argument) == int):
            stack.push(str(argument))
        else:
            print("Error: ItoS function can only accept integers.")
            exit()

def apply_rules():
    op = ["+", "-", "*", "/", "**", "gr", "ge", "ls", "le", "eq", "ne", "or", "&", "aug"]
    uop = ["neg", "not"]

    global control
    global current_environment

    while(len(control) > 0):
     
        symbol = control.pop()

        # Rule 1
        if type(symbol) == str and (symbol[0] == "<" and symbol[-1] == ">"):
            stack.push(lookup(symbol))

        # Rule 2
        elif type(symbol) == Lambda:
            temp = Lambda(symbol.number)
            temp.bounded_variable = symbol.bounded_variable
            temp.environment = current_environment
            stack.push(temp)

        # Rule 4
        elif (symbol == "gamma"):
            stack_symbol_1 = stack.pop()
            stack_symbol_2 = stack.pop()

            if (type(stack_symbol_1) == Lambda):
                current_environment = len(environments)
                
                lambda_number = stack_symbol_1.number
                bounded_variable = stack_symbol_1.bounded_variable
                parent_environment_number = stack_symbol_1.environment

                parent = environments[parent_environment_number]
                child = Environment(current_environment, parent)
                parent.add_child(child)
                environments.append(child)

                # Rule 11
                variable_list = bounded_variable.split(",")
                
                if (len(variable_list) > 1):
                    for i in range(len(variable_list)):
                        child.add_variable(variable_list[i], stack_symbol_2[i])
                else:
                    child.add_variable(bounded_variable, stack_symbol_2)

                stack.push(child.name)
                control.append(child.name)
                control += control_structures[lambda_number]

            # Rule 10
            elif (type(stack_symbol_1) == tuple):
                stack.push(stack_symbol_1[stack_symbol_2 - 1])

            # Rule 12
            elif (stack_symbol_1 == "Y*"):
                temp = Eta(stack_symbol_2.number)
                temp.bounded_variable = stack_symbol_2.bounded_variable
                temp.environment = stack_symbol_2.environment
                stack.push(temp)

            # Rule 13
            elif (type(stack_symbol_1) == Eta):
                temp = Lambda(stack_symbol_1.number)
                temp.bounded_variable = stack_symbol_1.bounded_variable
                temp.environment = stack_symbol_1.environment
                
                control.append("gamma")
                control.append("gamma")
                stack.push(stack_symbol_2)
                stack.push(stack_symbol_1)
                stack.push(temp)

            # Built-in functions
            elif stack_symbol_1 in builtInFunctions:
                built_in(stack_symbol_1, stack_symbol_2)
              
        # Rule 5
        elif type(symbol) == str and (symbol[0:2] == "e_"):
            stack_symbol = stack.pop()
            stack.pop()
            
            if (current_environment != 0):
                for element in reversed(stack):
                    if (type(element) == str and element[0:2] == "e_"):
                        current_environment = int(element[2:])
                        break
            stack.push(stack_symbol)

        # Rule 6
        elif (symbol in op):
            rand_1 = stack.pop()
            rand_2 = stack.pop()
            if (symbol == "+"): 
                stack.push(rand_1 + rand_2)
            elif (symbol == "-"):
                stack.push(rand_1 - rand_2)
            elif (symbol == "*"):
                stack.push(rand_1 * rand_2)
            elif (symbol == "/"):
                stack.push(rand_1 // rand_2)
            elif (symbol == "**"):
                stack.push(rand_1 ** rand_2)
            elif (symbol == "gr"):
                stack.push(rand_1 > rand_2)
            elif (symbol == "ge"):
                stack.push(rand_1 >= rand_2)
            elif (symbol == "ls"):
                stack.push(rand_1 < rand_2)
            elif (symbol == "le"):
                stack.push(rand_1 <= rand_2)
            elif (symbol == "eq"):
                stack.push(rand_1 == rand_2)
            elif (symbol == "ne"):
                stack.push(rand_1 != rand_2)
            elif (symbol == "or"):
                stack.push(rand_1 or rand_2)
            elif (symbol == "&"):
                stack.push(rand_1 and rand_2)
            elif (symbol == "aug"):
                if (type(rand_2) == tuple):
                    stack.push(rand_1 + rand_2)
                else:
                    stack.push(rand_1 + (rand_2,))

        # Rule 7
        elif (symbol in uop):
            rand = stack.pop()
            if (symbol == "not"):
                stack.push(not rand)
            elif (symbol == "neg"):
                stack.push(-rand)

        # Rule 8
        elif (symbol == "beta"):
            B = stack.pop()
            else_part = control.pop()
            then_part = control.pop()
            if (B):
                control += control_structures[then_part.number]
            else:
                control += control_structures[else_part.number]

        # Rule 9
        elif type(symbol) == Tau:
            n = symbol.number
            tau_list = []
            for i in range(n):
                tau_list.append(stack.pop())
            tau_tuple = tuple(tau_list)
            stack.push(tau_tuple)

        elif (symbol == "Y*"):
            stack.push(symbol)

    # Lambda expression becomes a lambda closure when its environment is determined.
    if type(stack[0]) == Lambda:
        stack[0] = "[lambda closure: " + str(stack[0].bounded_variable) + ": " + str(stack[0].number) + "]"
         
    if type(stack[0]) == tuple:          
        # The rpal.exe program prints the boolean values in lowercase. Our code must emulate this behaviour. 
        for i in range(len(stack[0])):
            if type(stack[0][i]) == bool:
                stack[0] = list(stack[0])
                stack[0][i] = str(stack[0][i]).lower()
                stack[0] = tuple(stack[0])
                
        # The rpal.exe program does not print the comma when there is only one element in the tuple.
        # Our code must emulate this behaviour.  
        if len(stack[0]) == 1:
            stack[0] = "(" + str(stack[0][0]) + ")"
        
        # The rpal.exe program does not print inverted commas when an element in the tuple is a string.
        # Our code must emulate this behaviour too. 
        else: 
            if any(type(element) == str for element in stack[0]):
                temp = "("
                for element in stack[0]:
                    temp += str(element) + ", "
                temp = temp[:-2] + ")"
                stack[0] = temp
                
    # The rpal.exe program prints the boolean values in lowercase. Our code must emulate this behaviour.    
    if stack[0] == True or stack[0] == False:
        stack[0] = str(stack[0]).lower()

# The following function is called from the myrpal.py file.
def get_result(file_name):
    global control

    st = standardize(file_name)
    
    generate_control_structure(st,0) 
    
    control.append(environments[0].name)
    control += control_structures[0]

    stack.push(environments[0].name)

    apply_rules()

    if print_present:
        print(stack[0])