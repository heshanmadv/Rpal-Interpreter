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

    # First, process children (post‐order)
    for child in root.children:
        make_standardized_tree(child)

    # Then, rewrite at this node if needed
    val = root.value

    # 1. let-binding: let (= X E1) E2  →  gamma (lambda X E2) E1
    if val == "let" and len(root.children) == 2 and root.children[0].value == "=":
        eq_node = root.children[0]
        E1 = eq_node.children[1]
        X_node = eq_node.children[0]
        E2 = root.children[1]

        # Build lambda node: lambda X E2
        lam = ASTNode("lambda")
        lam.add_child(X_node)
        lam.add_child(E2)

        # Rewire root into gamma
        root.value = "gamma"
        root.children = [lam, E1]
        return root

    # 2. where: where E1 (= X E2)  →  gamma lambda(X E2) E1, but swapped
    if val == "where" and len(root.children) == 2 and root.children[1].value == "=":
        E1 = root.children[0]
        eq_node = root.children[1]
        X_node = eq_node.children[0]
        E2 = eq_node.children[1]
        lam = ASTNode("lambda")
        lam.add_child(X_node)
        lam.add_child(E1)
        gamma_node = ASTNode("gamma")
        gamma_node.add_child(lam)
        gamma_node.add_child(E2)
        root.value = "gamma"
        root.children = [lam, E2]
        return root

    # 3. function_form: (function_form X1 X2 ... Xn E) → (= X1 (lambda X2 ... (lambda Xn E)...))
    if val == "function_form":
        # children: [X1, X2, ..., Xn, E]
        *params, body = root.children
        # Build nested lambdas right‐to‐left
        nested = body
        for p in reversed(params):
            lam = ASTNode("lambda")
            lam.add_child(p)
            lam.add_child(nested)
            nested = lam
        root.value = "="
        root.children = [params[0], nested]
        return root

    # 4. gamma with >2 children → nested gamma
    if val == "gamma" and len(root.children) > 2:
        # children: [E1, E2, E3, ..., En]
        *heads, last = root.children
        # Build nested left‐associative gamma: gamma(gamma(...(E1,E2)...),En)
        nested = heads[0]
        for nxt in heads[1:]:
            gm = ASTNode("gamma")
            gm.add_child(nested)
            gm.add_child(nxt)
            nested = gm
        gm_final = ASTNode("gamma")
        gm_final.add_child(nested)
        gm_final.add_child(last)
        return gm_final

    # 5. within: within (= X1 E1) (= X2 E2)  →  (= X2 gamma(lambda X1 E2) E1)
    if val == "within" and len(root.children) == 2:
        left = root.children[0]
        right = root.children[1]
        if left.value == "=" and right.value == "=":
            X1 = left.children[0]
            E1 = left.children[1]
            X2 = right.children[0]
            E2 = right.children[1]

            lam = ASTNode("lambda")
            lam.add_child(X1)
            lam.add_child(E2)
            gamma_node = ASTNode("gamma")
            gamma_node.add_child(lam)
            gamma_node.add_child(E1)

            root.value = "="
            root.children = [X2, gamma_node]
            return root

    # 6. '@' application: (@ E1 N E2) → gamma(gamma(N,E1),E2)
    if val == "@" and len(root.children) == 3:
        E1 = root.children[0]
        N = root.children[1]
        E2 = root.children[2]
        inner = ASTNode("gamma")
        inner.add_child(N)
        inner.add_child(E1)
        gm = ASTNode("gamma")
        gm.add_child(inner)
        gm.add_child(E2)
        return gm

    # 7. and: and [ (= Xi Ei ) ... ] → (= ( , X1 X2 ...) ( tau E1 E2 ... ) )
    if val == "and":
        # each child is an '=' node
        xs = [c.children[0] for c in root.children]
        es = [c.children[1] for c in root.children]
        comma_node = ASTNode(",")
        for x in xs:
            comma_node.add_child(x)
        tau_node = ASTNode("tau")
        for e in es:
            tau_node.add_child(e)
        root.value = "="
        root.children = [comma_node, tau_node]
        return root

    # 8. rec: rec (= X E) → (= X gamma(Y*, lambda X E) )
    if val == "rec" and len(root.children) == 1:
        eq_node = root.children[0]
        if eq_node.value == "=":
            X = eq_node.children[0]
            E = eq_node.children[1]
            lam = ASTNode("lambda")
            lam.add_child(X)
            lam.add_child(E)
            gamma_node = ASTNode("gamma")
            gamma_node.add_child(ASTNode("<Y*>"))
            gamma_node.add_child(lam)
            root.value = "="
            root.children = [X, gamma_node]
            return root

    return root
