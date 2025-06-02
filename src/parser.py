from __future__ import annotations
from typing import List, Optional
from src.rpal_token import Token, TokenType
from src.lexer import Lexer
from src.screener import Screener
from src.rpal_ast import ASTNode
from src.errors import SyntaxError, LexicalError


class Parser:
    """
    Implements a recursive‐descent parser for RPAL, building an AST of ASTNode objects.
    The grammar (phrase‐structure) is:

    E   -> 'let' D 'in' E           ⇒ 'let'
         | 'fn' Vb+ '.' E           ⇒ 'lambda'
         | Ew

    Ew  -> T 'where' Dr             ⇒ 'where'
         | T

    T   -> Ta (',' Ta)+             ⇒ 'tau'
         | Ta

    Ta  -> Ta 'aug' Tc              ⇒ 'aug'
         | Tc

    Tc  -> B '->' Tc '|' Tc         ⇒ '->'
         | B

    B   -> B 'or' Bt                ⇒ 'or'
         | Bt

    Bt  -> Bt '&' Bs                ⇒ '&'
         | Bs

    Bs  -> 'not' Bp                 ⇒ 'not'
         | Bp

    Bp  -> A ('gr'|'>' ) A          ⇒ 'gr'
         | A ('ge'|'>=') A          ⇒ 'ge'
         | A ('ls'|'<' ) A          ⇒ 'ls'
         | A ('le'|'<=') A          ⇒ 'le'
         | A 'eq' A                 ⇒ 'eq'
         | A 'ne' A                 ⇒ 'ne'
         | A

    A   -> A '+' At                 ⇒ '+'
         | A '-' At                 ⇒ '-'
         | '+' At                   ⇒ 'neg'
         | '-' At                   ⇒ 'neg'
         | At

    At  -> At '*' Af                ⇒ '*'
         | At '/' Af                ⇒ '/'
         | Af

    Af  -> Ap '**' Af               ⇒ '**'
         | Ap

    Ap  -> Ap '@' '<IDENTIFIER>' R  ⇒ '@'
         | R

    R   -> R Rn                     ⇒ 'gamma'
         | Rn

    Rn  -> '<IDENTIFIER>'
         | '<INTEGER>'
         | '<STRING>'
         | 'true'                   ⇒ '<true>'
         | 'false'                  ⇒ '<false>'
         | 'nil'                    ⇒ '<nil>'
         | 'dummy'                  ⇒ '<dummy>'
         | '(' E ')'

    D   -> Da 'within' D            ⇒ 'within'
         | Da

    Da  -> Dr ('and' Dr)+           ⇒ 'and'
         | Dr

    Dr  -> 'rec' Db                 ⇒ 'rec'
         | Db

    Db  -> Vl '=' E                 ⇒ '='
         | '<IDENTIFIER>' Vb+ '=' E ⇒ 'function_form'
         | '(' D ')'

    Vb  -> '<IDENTIFIER>'
         | '(' Vl ')'
         | '(' ')'                  ⇒ '()'

    Vl  -> '<IDENTIFIER>' (',' '<IDENTIFIER>')*   ⇒ tuple of identifiers
    """

    def __init__(self, source_code: str) -> None:
        self.lexer = Lexer(source_code)
        raw_tokens = self.lexer.tokenize()
        screener = Screener(raw_tokens)
        filtered, has_invalid, inv_tok = screener.screen()
        if has_invalid:
            raise LexicalError(
                f"Invalid token '{inv_tok.content}'", inv_tok.line)
        self.tokens: List[Token] = filtered
        self.current: int = 0

    # ─────────────────────────────────────────────────────────────────────
    # Public entry point
    # ─────────────────────────────────────────────────────────────────────

    def parse(self) -> ASTNode:
        """
        Entry point: parse an entire expression (E). At the end, exactly one ASTNode must remain.
        """
        node = self.E()
        if self.current < len(self.tokens):
            extra = self.tokens[self.current]
            raise SyntaxError("end of input", extra.content, extra.line)
        return node

    # ─────────────────────────────────────────────────────────────────────
    # Helper methods for token navigation
    # ─────────────────────────────────────────────────────────────────────

    def _at_end(self) -> bool:
        return self.current >= len(self.tokens)

    def _peek(self) -> Token:
        if self._at_end():
            last = self.tokens[-1]
            return Token("<EOF>", "<EOF>", last.line)
        return self.tokens[self.current]

    def _advance(self) -> Token:
        if not self._at_end():
            self.current += 1
        return self.tokens[self.current - 1]

    def _match(self, expected: str) -> Token:
        tok = self._peek()
        if tok.content == expected:
            return self._advance()
        raise SyntaxError(expected, tok.content, tok.line)

    def _match_type(self, expected_type: str) -> Token:
        tok = self._peek()
        if tok.type == expected_type:
            return self._advance()
        raise SyntaxError(expected_type, tok.type, tok.line)

    # ─────────────────────────────────────────────────────────────────────
    # Grammar productions (each returns an ASTNode)
    # ─────────────────────────────────────────────────────────────────────

    def E(self) -> ASTNode:
        """
        E → 'let' D 'in' E       |       'fn' Vb+ '.' E       |       Ew
        """
        tok = self._peek()
        if tok.content == "let":
            self._advance()  # consume 'let'
            left = self.D()
            self._match("in")
            right = self.E()
            node = ASTNode("let")
            node.add_child(left)
            node.add_child(right)
            return node

        elif tok.content == "fn":
            self._advance()  # consume 'fn'
            var_nodes: List[ASTNode] = []
            # Must have Vb+  → at least one Vb
            if not (self._peek().type == "<IDENTIFIER>" or self._peek().content == "("):
                raise SyntaxError("Vb", self._peek().content,
                                  self._peek().line)

            while self._peek().type == "<IDENTIFIER>" or self._peek().content == "(":
                var_nodes.append(self.Vb())

            self._match(".")
            body = self.E()
            lam = ASTNode("lambda")
            for v in var_nodes:
                lam.add_child(v)
            lam.add_child(body)
            return lam

        else:
            return self.Ew()

    def Ew(self) -> ASTNode:
        """
        Ew → T 'where' Dr       |       T
        """
        tnode = self.T()
        if self._peek().content == "where":
            self._advance()
            drnode = self.Dr()
            node = ASTNode("where")
            node.add_child(tnode)
            node.add_child(drnode)
            return node
        return tnode

    def T(self) -> ASTNode:
        """
        T → Ta ( ',' Ta )+     ⇒ 'tau'
          | Ta
        """
        ta_nodes: List[ASTNode] = [self.Ta()]
        while self._peek().content == ",":
            self._advance()
            ta_nodes.append(self.Ta())
        if len(ta_nodes) > 1:
            tau = ASTNode("tau")
            for ch in ta_nodes:
                tau.add_child(ch)
            return tau
        return ta_nodes[0]

    def Ta(self) -> ASTNode:
        """
        Ta → Ta 'aug' Tc      ⇒ 'aug'
           | Tc
        """
        node = self.Tc()
        while self._peek().content == "aug":
            self._advance()
            right = self.Tc()
            parent = ASTNode("aug")
            parent.add_child(node)
            parent.add_child(right)
            node = parent
        return node

    def Tc(self) -> ASTNode:
        """
        Tc → B '->' Tc '|' Tc   ⇒ '->'
           | B
        """
        left = self.B()
        if self._peek().content == "->":
            self._advance()
            mid = self.Tc()
            self._match("|")
            right = self.Tc()
            parent = ASTNode("->")
            parent.add_child(left)
            parent.add_child(mid)
            parent.add_child(right)
            return parent
        return left

    def B(self) -> ASTNode:
        """
        B → B 'or' Bt      ⇒ 'or'
          | Bt
        """
        node = self.Bt()
        while self._peek().content == "or":
            self._advance()
            right = self.Bt()
            parent = ASTNode("or")
            parent.add_child(node)
            parent.add_child(right)
            node = parent
        return node

    def Bt(self) -> ASTNode:
        """
        Bt → Bt '&' Bs     ⇒ '&'
           | Bs
        """
        node = self.Bs()
        while self._peek().content == "&":
            self._advance()
            right = self.Bs()
            parent = ASTNode("&")
            parent.add_child(node)
            parent.add_child(right)
            node = parent
        return node

    def Bs(self) -> ASTNode:
        """
        Bs → 'not' Bp      ⇒ 'not'
           | Bp
        """
        if self._peek().content == "not":
            self._advance()
            child = self.Bp()
            parent = ASTNode("not")
            parent.add_child(child)
            return parent
        return self.Bp()

    def Bp(self) -> ASTNode:
        """
        Bp → A ('gr'|'>' ) A   ⇒ 'gr'
           | A ('ge'|'>=') A   ⇒ 'ge'
           | A ('ls'|'<' ) A   ⇒ 'ls'
           | A ('le'|'<=') A   ⇒ 'le'
           | A 'eq' A          ⇒ 'eq'
           | A 'ne' A          ⇒ 'ne'
           | A
        """
        node = self.A()
        cmp_ops = {"gr", ">", "ge", ">=", "ls", "<", "le", "<=", "eq", "ne"}
        if self._peek().content in cmp_ops:
            op_tok = self._advance().content
            # Normalize multi‐character tokens: '>'→'gr', '>='→'ge', '<'→'ls', '<='→'le'
            if op_tok == ">":
                op = "gr"
            elif op_tok == ">=":
                op = "ge"
            elif op_tok == "<":
                op = "ls"
            elif op_tok == "<=":
                op = "le"
            else:
                op = op_tok  # one of gr, ge, ls, le, eq, ne
            right = self.A()
            parent = ASTNode(op)
            parent.add_child(node)
            parent.add_child(right)
            return parent
        return node

    def A(self) -> ASTNode:
        """
        A → A '+' At        ⇒ '+'
          | A '-' At        ⇒ '-'
          | '+' At          ⇒ 'neg'
          | '-' At          ⇒ 'neg'
          | At
        """
        # Handle unary +/−
        if self._peek().content in ("+", "-") and self.tokens[self.current + 1].type != "<INTEGER>":
            sign = self._advance().content
            node = self.At()
            parent = ASTNode(sign)
            parent.add_child(ASTNode("0"))  # unary expresses as (0 +/− At)
            parent.add_child(node)
            return parent

        node = self.At()
        while self._peek().content in ("+", "-"):
            op = self._advance().content
            right = self.At()
            parent = ASTNode(op)
            parent.add_child(node)
            parent.add_child(right)
            node = parent
        return node

    def At(self) -> ASTNode:
        """
        At → At '*' Af     ⇒ '*'
           | At '/' Af     ⇒ '/'
           | Af
        """
        node = self.Af()
        while self._peek().content in ("*", "/"):
            op = self._advance().content
            right = self.Af()
            parent = ASTNode(op)
            parent.add_child(node)
            parent.add_child(right)
            node = parent
        return node

    def Af(self) -> ASTNode:
        """
        Af → Ap '**' Af    ⇒ '**'
           | Ap
        """
        node = self.Ap()
        if self._peek().content == "**":
            self._advance()
            right = self.Af()
            parent = ASTNode("**")
            parent.add_child(node)
            parent.add_child(right)
            node = parent
        return node

    def Ap(self) -> ASTNode:
        """
        Ap → Ap '@' '<IDENTIFIER>' R   ⇒ '@'
           | R
        """
        node = self.R()
        while self._peek().content == "@":
            self._advance()
            ident_tok = self._match_type("<IDENTIFIER>")
            ident_node = ASTNode(f"<ID:{ident_tok.content}>")
            rhs = self.R()
            parent = ASTNode("@")
            parent.add_child(ident_node)
            parent.add_child(node)
            parent.add_child(rhs)
            node = parent
        return node

    def R(self) -> ASTNode:
        """
        R → R Rn     ⇒ 'gamma'
          | Rn
        """
        node = self.Rn()
        while (
            self._peek().type == "<IDENTIFIER>"
            or self._peek().type == "<INTEGER>"
            or self._peek().type == "<STRING>"
            or self._peek().content in ("true", "false", "nil", "dummy", "(")
        ):
            right = self.Rn()
            parent = ASTNode("gamma")
            parent.add_child(node)
            parent.add_child(right)
            node = parent
        return node

    def Rn(self) -> ASTNode:
        """
        Rn → '<IDENTIFIER>'
           | '<INTEGER>'
           | '<STRING>'
           | 'true'   ⇒ '<true>'
           | 'false'  ⇒ '<false>'
           | 'nil'    ⇒ '<nil>'
           | 'dummy'  ⇒ '<dummy>'
           | '(' E ')'
        """
        tok = self._peek()
        if tok.type == "<IDENTIFIER>":
            self._advance()
            return ASTNode(f"<ID:{tok.content}>")
        if tok.type == "<INTEGER>":
            self._advance()
            return ASTNode(f"<INT:{tok.content}>")
        if tok.type == "<STRING>":
            self._advance()
            return ASTNode(f"<STR:{tok.content}>")
        if tok.content in ("true", "false", "nil", "dummy"):
            val = tok.content
            self._advance()
            return ASTNode(f"<{val}>")
        if tok.content == "(":
            self._advance()
            node = self.E()
            self._match(")")
            return node
        raise SyntaxError(
            "identifier, integer, string, 'true', 'false', 'nil', 'dummy', or '('", tok.content, tok.line)

    def D(self) -> ASTNode:
        """
        D → Da 'within' D     ⇒ 'within'
          | Da
        """
        node = self.Da()
        if self._peek().content == "within":
            self._advance()
            right = self.D()
            parent = ASTNode("within")
            parent.add_child(node)
            parent.add_child(right)
            return parent
        return node

    def Da(self) -> ASTNode:
        """
        Da → Dr ('and' Dr)+   ⇒ 'and'
           | Dr
        """
        nodes: List[ASTNode] = [self.Dr()]
        while self._peek().content == "and":
            self._advance()
            nodes.append(self.Dr())
        if len(nodes) > 1:
            parent = ASTNode("and")
            for n in nodes:
                parent.add_child(n)
            return parent
        return nodes[0]

    def Dr(self) -> ASTNode:
        """
        Dr → 'rec' Db       ⇒ 'rec'
           | Db
        """
        if self._peek().content == "rec":
            self._advance()
            child = self.Db()
            parent = ASTNode("rec")
            parent.add_child(child)
            return parent
        return self.Db()

    def Db(self) -> ASTNode:
        """
        Db → Vl '=' E                         ⇒ '='
           | '<IDENTIFIER>' Vb+ '=' E         ⇒ 'function_form'
           | '(' D ')'                        ⇒ grouped definition
        """
        # Case: '(' D ')'
        if self._peek().content == "(":
            self._advance()              # consume '('
            node = self.D()
            self._match(")")
            return node

        # Must start with an <IDENTIFIER> for either binding or function_form
        id_tok = self._match_type("<IDENTIFIER>")
        id_node = ASTNode(f"<ID:{id_tok.content}>")
        nxt_tok = self._peek()

        # Case: simple binding X = E
        if nxt_tok.content == "=":
            self._advance()              # consume '='
            rhs = self.E()
            parent = ASTNode("=")
            parent.add_child(id_node)
            parent.add_child(rhs)
            return parent

        # Case: function_form: <IDENTIFIER> Vb+ '=' E
        # i.e. at least one Vb must follow
        if nxt_tok.type == "<IDENTIFIER>" or nxt_tok.content == "(":
            var_nodes: List[ASTNode] = []
            # parse one or more Vb
            while self._peek().type == "<IDENTIFIER>" or self._peek().content == "(":
                var_nodes.append(self.Vb())
            self._match("=")
            rhs = self.E()
            parent = ASTNode("function_form")
            parent.add_child(id_node)
            for v in var_nodes:
                parent.add_child(v)
            parent.add_child(rhs)
            return parent

        # If neither '=' nor a Vb follows, it's a syntax error
        raise SyntaxError("'=' or function form arguments",
                          nxt_tok.content, nxt_tok.line)

    def Vb(self) -> ASTNode:
        """
        Vb → '<IDENTIFIER>'
           | '(' Vl ')'     ⇒ tuple of identifiers
           | '(' ')'        ⇒ '()'  (empty tuple)
        """
        # Case: identifier
        if self._peek().type == "<IDENTIFIER>":
            tok = self._advance()
            return ASTNode(f"<ID:{tok.content}>")

        # Case: '(' Vl ')'  or  '(' ')'
        if self._peek().content == "(":
            self._advance()                # consume '('
            # Check for '()' (empty tuple)
            if self._peek().content == ")":
                self._advance()            # consume ')'
                node = ASTNode("()")
                return node

            # Otherwise, parse Vl
            vl_node = self.Vl()
            self._match(")")
            # Flatten Vl's children into a single node for binding purposes
            node = ASTNode("tuple_vars")
            for child in vl_node.children:
                node.add_child(child)
            return node

        raise SyntaxError(
            "identifier or '('", self._peek().content, self._peek().line)

    def Vl(self) -> ASTNode:
        """
        Vl → '<IDENTIFIER>' ( ',' '<IDENTIFIER>' )*
        """
        first_tok = self._match_type("<IDENTIFIER>")
        var_nodes: List[ASTNode] = [ASTNode(f"<ID:{first_tok.content}>")]
        while self._peek().content == ",":
            self._advance()                        # consume ','
            next_tok = self._match_type("<IDENTIFIER>")
            var_nodes.append(ASTNode(f"<ID:{next_tok.content}>"))
        node = ASTNode("tuple_vars")
        for v in var_nodes:
            node.add_child(v)
        return node
