from __future__ import annotations
from src.rpal_ast import ASTNode
from src.parser import Parser


def standardize(source_code: str) -> ASTNode:
    """
    Parses the source into an AST, then applies make_standardized_tree to obtain an ST.
    """
    parser = Parser(source_code)
    ast_root = parser.parse()
    return make_standardized_tree(ast_root)


def make_standardized_tree(root: ASTNode) -> ASTNode:
    """
    Recursively descends the AST, rewrites syntactic sugar into core primitives.
    """

    for child in root.children:
        make_standardized_tree(child)

    if root.value == "let" and root.children[0].value == "=":
        '''
                 let                gamma
                /   \               /    \    
               =     P   =>       lambda  E               
              / \                /      \'
             X   E              X       P
        '''
        child_0 = root.children[0]
        child_1 = root.children[1]

        root.children[1] = child_0.children[1]
        root.children[0].children[1] = child_1
        root.children[0].value = "lambda"
        root.value = "gamma"

    elif root.value == "where" and root.children[1].value == "=":
        '''
                 where                gamma 
                 /   \                /    \
                E     P     =>      lambda  E
                     / \             /  \
                    X   E           X    P
        '''
        child_0 = root.children[0]
        child_1 = root.children[1]

        root.children[0] = child_1.children[1]
        root.children[1].children[1] = child_0
        root.children[1].value = "lambda"
        root.children[0], root.children[1] = root.children[1], root.children[0]
        root.value = "gamma"

    elif root.value == "function_form":
        '''
                 function_form                  =
                 /   |    \                    / \
                P    V+    E     =>           P   +lambda
                                                   /   \
                                                  V    .E                  
        '''
        expression = root.children.pop()

        current_node = root
        for i in range(len(root.children) - 1):
            lambda_node = ASTNode("lambda")
            child = root.children.pop(1)
            lambda_node.children.append(child)
            current_node.children.append(lambda_node)
            current_node = lambda_node

        current_node.children.append(expression)
        root.value = "="

    elif root.value == "gamma" and len(root.children) > 2:
        expression = root.children.pop()

        current_node = root
        for i in range(len(root.children) - 1):
            lambda_node = ASTNode("lambda")
            child = root.children.pop(1)
            lambda_node.children.append(child)
            current_node.children.append(lambda_node)
            current_node = lambda_node

        current_node.children.append(expression)

    elif root.value == "within" and root.children[0].value == root.children[1].value == "=":
        '''
                    within                =
                    /    \               / \
                   =      =     =>      X2   gamma
                  / \    / \                 /   \
                 X1  E1  X2 E2            lambda  E1 
                                          /    \
                                         X1    E2    
        '''
        child_0 = root.children[1].children[0]
        child_1 = ASTNode("gamma")

        child_1.children.append(ASTNode("lambda"))
        child_1.children.append(root.children[0].children[1])
        child_1.children[0].children.append(root.children[0].children[0])
        child_1.children[0].children.append(root.children[1].children[1])

        root.children[0] = child_0
        root.children[1] = child_1
        root.value = "="

    elif root.value == "@":
        '''
                    @                gamma
                  / | \              /   \
                E1  N  E2    =>    gamma  E2
                                   /   \
                                  N     E1
        '''
        expression = root.children.pop(0)
        identifier = root.children[0]

        gamma_node = ASTNode("gamma")
        gamma_node.children.append(identifier)
        gamma_node.children.append(expression)

        root.children[0] = gamma_node

        root.value = "gamma"

    elif root.value == "and":
        '''
                    and             =
                     |             / \
                    =++    =>     ,   tau
                    / \           |    |
                   X   E         X++  E++

        '''
        child_0 = ASTNode(",")
        child_1 = ASTNode("tau")

        for child in root.children:
            child_0.children.append(child.children[0])
            child_1.children.append(child.children[1])

        root.children.clear()

        root.children.append(child_0)
        root.children.append(child_1)

        root.value = "="

    elif root.value == "rec":
        '''
                    rec             =
                     |             / \
                     =     =>     X   gamma
                    / \               /   \
                   X   E            Ystar lambda
                                          /    \
                                         X      E
        '''
        temp = root.children.pop()
        temp.value = "lambda"

        gamma_node = ASTNode("gamma")
        gamma_node.children.append(ASTNode("<Y*>"))
        gamma_node.children.append(temp)

        root.children.append(temp.children[0])
        root.children.append(gamma_node)

        root.value = "="

    return root
