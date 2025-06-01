from src.screener import screener
from src.stack import Stack
from src.node import *

# A stack containing nodes
stack = Stack("AST")

# This function is used to read the expected token. 
def read(target_token):
    current = tokens[0]
    if current.content != target_token:
        print(f"Syntax error in line {current.line}: Expected {target_token} but got {current.content}")
        exit(1)
     
    if not current.is_last_token:
        del tokens[0]   
        
    else:
        if current.type != ")":
            current.type = ")"    
           


# This function is used to print the abstract syntax tree in preorder traversal.    
def print_ASTtree(root):
    preorder_traversal(root)

# This function is used to build the abstract syntax tree.
def build_tree(value, num_children):
    node = Node(value)
    node.children = [None] * num_children
    
    for i in range (0, num_children):
        if stack.is_empty():
            print("Stack is empty")
            exit(1)
        node.children[num_children - i - 1] = stack.pop()
        
    stack.push(node)
 

 

def parse(file_name):
    global tokens
    tokens, has_invalid_token, invalid_token = screener(file_name)
    
    # If there are invalid tokens, we cannot proceed with the parsing.
    if has_invalid_token:
        print("Invalid token present in line " + str(invalid_token.line) + ": " + str(invalid_token.content))
        exit(1)

    
    E()
    
    if not stack.is_empty():
        root = stack.pop()
    else:
        print("Stack is empty")
        exit(1)
        
    return root
 
############################################################## 
def E():      
    # E -> 'let' D 'in' E 
    if tokens[0].content == "let":
        read("let")
        D()
        
        if tokens[0].content == "in":
            read("in")
            E()
            build_tree("let", 2)
        else:
            print("Syntax error in line " + str(tokens[0].line) + ": 'in' expected")
            exit(1)
    
    # E -> 'fn'  Vb+ '.' E    
    elif tokens[0].content == "fn":
        read("fn")
        n = 0

        while tokens[0].type == "<IDENTIFIER>" or tokens[0].type == "(": 
            Vb()
            n += 1
            
        if n == 0:
            print("Syntax error in line " + str(tokens[0].line) + ": Identifier or '(' expected")
            exit(1)
            
        if tokens[0].content == ".":
            read(".")
            E()
            build_tree("lambda", n + 1)
        else:
            print("Syntax error in line " + str(tokens[0].line) + ": '.' expected")
            exit(1)
             
    # E  ->  Ew    
    else:
        Ew()

##############################################################
def Ew():
    # Ew -> T    
    T()
    
    # Ew -> T 'where' Dr   
    if tokens[0].content == "where":
        read("where")
        Dr()
        build_tree("where", 2)  
        
##############################################################
def T():     
    # T -> Ta
    Ta()
    
    # T -> Ta (','  Ta)+
    n = 0
    while tokens[0].content == ",":
        read(",")
        Ta()
        n += 1
        
    if n > 0:
        build_tree("tau", n+1)
        
##############################################################      
def Ta():  
    # Ta -> Tc
    Tc()
    
    # Ta -> Ta 'aug' Tc 
    while tokens[0].content == "aug":
        read("aug")
        Tc()
        build_tree("aug", 2)  
        
##############################################################
def Tc():   
    # Tc -> B
    B()
    
    # Tc -> B '->' Tc '|' Tc
    if tokens[0].content == "->":  
        read("->")
        Tc()
        
        if tokens[0].content == "|":
            read("|")
            Tc()
            build_tree("->", 3)
        else:
            print("Syntax error in line " + str(tokens[0].line) + ": '|' expected")
            exit(1)
            
##############################################################
def B():
    # B -> Bt
    Bt()
    
    # B -> B 'or' Bt
    while tokens[0].content == "or":
        read("or")
        Bt()
        build_tree("or", 2) 

##############################################################
def Bt():    
    # Bt -> Bs
    Bs()
    
    # Bt -> Bt '&' Bs
    while tokens[0].content == "&":
        read("&")
        Bs()
        build_tree("&", 2)
        
##############################################################
def Bs():
    # Bs -> 'not' Bp
    if tokens[0].content == "not":
        read("not")
        Bp()
        build_tree("not", 1)
        
    # Bs -> Bp
    else:
        Bp()
        
##############################################################
def Bp():           
    # Bp -> A
    A()
    
    # Bp -> A ('gr' | '>' ) A
    if tokens[0].content == "gr" or tokens[0].content == ">":
        read(tokens[0].content)
        A()
        build_tree("gr", 2)
        
    # Bp -> A ('ge' | '>=' ) A
    elif tokens[0].content == "ge" or tokens[0].content == ">=":
        read(tokens[0].content)
        A()
        build_tree("ge", 2)
        
    # Bp -> A ('ls' | '<' ) A
    elif tokens[0].content == "ls" or tokens[0].content == "<":
        read(tokens[0].content)
        A()
        build_tree("ls", 2)
        
    # Bp -> A ('le' | '<=' ) A
    elif tokens[0].content == "le" or tokens[0].content == "<=":
        read(tokens[0].content)
        A()
        build_tree("le", 2)
        
    # Bp -> A 'eq' A
    elif tokens[0].content == "eq":
        read("eq")
        A()
        build_tree("eq", 2)
        
    # Bp -> A 'ne' A
    elif tokens[0].content == "ne":
        read("ne")
        A()
        build_tree("ne", 2)

##############################################################
def A():
    # A -> '+' At
    if tokens[0].content=="+":
        read("+")
        At()
        
    # A -> '-' At
    elif tokens[0].content=="-":
        read("-")
        At()
        build_tree("neg", 1)
        
    # A -> At
    else:
        At()
        
    while tokens[0].content in ["+", "-"]:
        # A -> A '+' At
        if tokens[0].content=="+":
            read("+")
            At()
            build_tree("+", 2)
            
        # A -> A '-' At
        else:
            read("-")
            At()
            build_tree("-", 2)
    
##############################################################
def At():
    # At -> Af
    Af()
    
    while tokens[0].content in ["*", "/"]:
        # At -> At '*' Af
        if tokens[0].content=="*":
            read("*")
            Af()
            build_tree("*", 2)
            
        # At -> At '/' Af
        else:
            read("/")
            Af()
            build_tree("/", 2)

##############################################################
def Af():    
    # Af -> Ap 
    Ap()
    
    # Af -> Ap '**' Af
    if tokens[0].content == "**":     
        read("**")
        Af()
        build_tree("**", 2)
 
##############################################################    
def Ap():
    # Ap -> R
    R()
    
    # Ap -> Ap '@' <IDENTIFIER> R
    while tokens[0].content == "@":
        read("@")
        
        if tokens[0].type == "<IDENTIFIER>":
            build_tree("<ID:" + tokens[0].content + ">", 0)
            read(tokens[0].content)
            R()
            build_tree("@", 3)            
        else:
            print("Syntax error in line " + str(tokens[0].line) + ": Identifier expected")
            exit(1)
    
##############################################################
def R():
    # R -> Rn
    Rn()
    
    # R -> R Rn
    while  tokens[0].type in ["<IDENTIFIER>", "<INTEGER>", "<STRING>"] or tokens[0].content in ["true", "false","nil", "(", "dummy"]: 
        Rn()
        build_tree("gamma", 2)

##############################################################
def Rn():   
    value = tokens[0].content
    
    # Rn -> <IDENTIFIER>
    if tokens[0].type == "<IDENTIFIER>":
        read(value)
        build_tree("<ID:" + value + ">", 0)
    
    # Rn -> <INTEGER>    
    elif tokens[0].type == "<INTEGER>":
        read(value)
        build_tree("<INT:" + value + ">", 0)
        
    # Rn -> <STRING>    
    elif tokens[0].type == "<STRING>":
        read(value)
        build_tree("<STR:" + value + ">", 0)
        
    # Rn -> 'true'
    #    -> 'false'
    #    -> 'nil'
    #    -> 'dummy'    
    elif value in ["true", "false", "nil", "dummy"]:
        read(value)
        build_tree("<" + value + ">", 0)
      
    # Rn -> '(' E ')'    
    elif value == "(":
        read("(")
        E()
        
        if tokens[0].content == ")":     
            read(")")
        else:
            print("Syntax error in line " + str(tokens[0].line) + ": ')' expected")
            exit(1)
            
    else:
        print("Syntax error in line " + str(tokens[0].line) + ": Identifier, Integer, String, 'true', 'false', 'nil', 'dummy' or '(' expected")
        exit(1)

##############################################################
def D():
    # D -> Da
    Da()
    
    # D -> Da 'within' D
    if tokens[0].content == "within":
        read("within")
        D()
        build_tree("within", 2)
    
##############################################################
def Da():
    # Da -> Dr
    Dr()
    
    # Da -> Dr ('and' Dr)+
    n = 0
    while tokens[0].content == "and":
        read("and")
        Dr()
        n += 1
        
    if n > 0:  
        build_tree("and", n + 1)
    
##############################################################
def Dr():
    # Dr -> 'rec' Db
    if tokens[0].content == "rec":
        read("rec")
        Db()
        build_tree("rec", 1)
        
    # Dr -> Db
    else:
        Db()
    
##############################################################
def Db():    
    value = tokens[0].content
    
    # Db -> '(' D ')'
    if value == "(":
        read("(")
        D()
        
        if tokens[0].content == ")":
            read(")")
        else:
            print("Syntax error in line " + str(tokens[0].line) + ": ')' expected")
            exit(1)

    elif tokens[0].type == "<IDENTIFIER>":
        read(value)
        build_tree("<ID:" + value + ">", 0)  

        # Db -> <IDENTIFIER> Vb+ '=' E
        if tokens[0].content in [",", "="]:  
            Vl()
            read("=")
            E()
            build_tree("=", 2)
        
        # Db -> Vl '=' E
        else: 
            n = 0
        
            while tokens[0].type == "<IDENTIFIER>" or tokens[0].type == "(":
                Vb()
                n += 1
                
            if n == 0:
                print("Syntax error in line " + str(tokens[0].line) + ": Identifier or '(' expected")
                exit(1)    
                
            if tokens[0].content == "=":
                read("=")
                E()
                build_tree("function_form", n + 2)
            else:
                print("Syntax error in line " + str(tokens[0].line) + ": '=' expected")
                exit(1)

##############################################################
def Vb(): 
    # Vb -> <IDENTIFIER>
    #    -> '(' Vl ')'
    #    -> '(' ')' 
    
    value_1 = tokens[0].content 

    # Vb -> <IDENTIFIER>
    if tokens[0].type == "<IDENTIFIER>":
        read(value_1)
        build_tree("<ID:" + value_1 + ">", 0)     
        
    elif value_1 == "(":
        read("(")
        
        value_2 = tokens[0].content 
        
        # Vb -> '(' ')'
        if value_2 == ")":
            read(")")
            build_tree("()", 0)
        
        # Vb -> '(' Vl ')'
        elif tokens[0].type == "<IDENTIFIER>": 
            read(value_2)
            build_tree("<ID:" + value_2 + ">", 0)    
            Vl()
            
            if tokens[0].content == ")":
                read(")")
            else:
                print("Syntax error in line " + str(tokens[0].line) + ": ')' expected")
                exit(1)
        else:
            print("Syntax error in line " + str(tokens[0].line) + ": Identifier or ')' expected")
            exit(1)
    else:
        print("Syntax error in line " + str(tokens[0].line) + ": Identifier or '(' expected")
        exit(1)
    
##############################################################
def Vl():
    # Vl -> <IDENTIFIER> (',' <IDENTIFIER>)*   
    n = 0
    
    while tokens[0].content == ",":
        read(",")
        
        if tokens[0].type == "<IDENTIFIER>":
            value = tokens[0].content
            read(value)
            build_tree("<ID:" + value + ">", 0)    
            n += 1
        else:
            print("Syntax error in line " + str(tokens[0].line) + ": Identifier expected")
            
    if n > 0:
        build_tree(",", n + 1) 