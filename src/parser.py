from __future__ import annotations
from typing import List
from src.rpal_token import Token, TokenType
from src.lexer import Lexer
from src.screener import Screener
from src.rpal_ast import ASTNode
from src.errors import SyntaxError, LexicalError


class Parser:
    """
    Recursive‐descent parser for RPAL, producing an AST of ASTNode objects.
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
        Parse an entire expression (E). At the end, exactly one ASTNode remains.
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
    # Grammar productions (return ASTNode)
    # ─────────────────────────────────────────────────────────────────────

    def E(self) -> ASTNode:
        """
        E → 'let' D 'in' E       |       'fn' Vb+ '.' E       |       Ew
        """
        tok = self._peek()
        if tok.content == "let":
            self._match("let")
            left = self.D()
            self._match("in")
            right = self.E()
            node = ASTNode("let")
            node.add_child(left)
            node.add_child(right)
            return node

        elif tok.content == "fn":
            self._match("fn")
            var_nodes: List[ASTNode] = []
            # Must have at least one Vb
            if not (self._peek().type == "<IDENTIFIER>" or self._peek().content == "("):
                raise SyntaxError("Vb", self._peek().content,
                                  self._peek().line)

            # Collect one or more Vb (each returns list of ID or ',' nodes)
            while self._peek().type == "<IDENTIFIER>" or self._peek().content == "(":
                vb_list = self.Vb_list()
                var_nodes.extend(vb_list)

            self._match(".")
            body = self.E()
            lam = ASTNode("lambda")
            # First children: all var_nodes
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
            self._match("where")
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
        comma_count = 0
        while self._peek().content == ",":
            self._match(",")
            ta_nodes.append(self.Ta())
            comma_count += 1
        if comma_count > 0:
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
            self._match("aug")
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
            self._match("->")
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
            self._match("or")
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
            self._match("&")
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
            self._match("not")
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
            if op_tok == ">":
                op = "gr"
            elif op_tok == ">=":
                op = "ge"
            elif op_tok == "<":
                op = "ls"
            elif op_tok == "<=":
                op = "le"
            else:
                op = op_tok
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
        # Unary +/− when not followed by an integer literal
        if self._peek().content in ("+", "-") and (
            self.current + 1 < len(self.tokens)
            and self.tokens[self.current + 1].type != "<INTEGER>"
        ):
            sign = self._advance().content
            node = self.At()
            parent = ASTNode(sign)
            parent.add_child(ASTNode("0"))
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
            self._match("**")
            right = self.Af()
            parent = ASTNode("**")
            parent.add_child(node)
            parent.add_child(right)
            node = parent
        return node

    def Ap(self) -> ASTNode:
        """
        Ap → R
        | Ap '@' <IDENTIFIER> R  ⇒ '@'
        """
        node = self.R()
        while self._peek().content == "@":
            self._match("@")

            # Next must be an <IDENTIFIER>
            ident_tok = self._match_type("<IDENTIFIER>")
            ident_node = ASTNode(f"<ID:{ident_tok.content}>")
            rhs = self.R()

            parent = ASTNode("@")
            parent.children.append(node)        # ← left subexpression
            parent.children.append(ident_node)  # ← identifier
            parent.children.append(rhs)         # ← right subexpression
            node = parent

        return node

    def R(self) -> ASTNode:
        """
        R → R Rn     ⇒ 'gamma'
          | Rn
        """
        node = self.Rn()
        while (
            self._peek().type in ["<IDENTIFIER>", "<INTEGER>", "<STRING>"]
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
            self._match_type("<IDENTIFIER>")
            return ASTNode(f"<ID:{tok.content}>")
        if tok.type == "<INTEGER>":
            self._match_type("<INTEGER>")
            return ASTNode(f"<INT:{tok.content}>")
        if tok.type == "<STRING>":
            self._match_type("<STRING>")
            return ASTNode(f"<STR:{tok.content}>")
        if tok.content in ("true", "false", "nil", "dummy"):
            val = tok.content
            self._advance()
            return ASTNode(f"<{val}>")
        if tok.content == "(":
            self._match("(")
            node = self.E()
            self._match(")")
            return node
        raise SyntaxError(
            "identifier, integer, string, 'true', 'false', 'nil', 'dummy', or '('",
            tok.content,
            tok.line,
        )

    def D(self) -> ASTNode:
        """
        D → Da 'within' D       ⇒ 'within'
          | Da
        """
        node = self.Da()
        if self._peek().content == "within":
            self._match("within")
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
        count = 0
        while self._peek().content == "and":
            self._match("and")
            nodes.append(self.Dr())
            count += 1
        if count > 0:
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
            self._match("rec")
            child = self.Db()
            parent = ASTNode("rec")
            parent.add_child(child)
            return parent
        return self.Db()

    def Db(self) -> ASTNode:
        """
        Db → '(' D ')'                         ⇒ grouped definition
           | <IDENTIFIER> Vb* '=' E            ⇒ 'function_form' (or simple =)
           | Vl '=' E                          ⇒ '=' (tuple‐binding)
        """
        # Case: '(' D ')'
        if self._peek().content == "(":
            self._match("(")
            node = self.D()
            self._match(")")
            return node

        # Next must be an <IDENTIFIER>
        id_tok = self._match_type("<IDENTIFIER>")
        id_node = ASTNode(f"<ID:{id_tok.content}>")

        # If next is '=', it's a simple binding X = E
        if self._peek().content == "=":
            self._match("=")
            rhs = self.E()
            parent = ASTNode("=")
            parent.add_child(id_node)
            parent.add_child(rhs)
            return parent

        # Otherwise: function_form <IDENTIFIER> Vb+ '=' E
        var_nodes: List[ASTNode] = []
        while self._peek().type == "<IDENTIFIER>" or self._peek().content == "(":
            var_nodes.extend(self.Vb_list())

        self._match("=")
        rhs = self.E()

        parent = ASTNode("function_form")
        parent.add_child(id_node)

        if len(var_nodes) == 1 and var_nodes[0].value == ",":
            parent.add_child(var_nodes[0])
        else:
            for v in var_nodes:
                parent.add_child(v)

        parent.add_child(rhs)
        return parent

    def Vb_list(self) -> List[ASTNode]:
        """
        Parses one Vb but returns a list of ASTNode(s):
          Vb_list → '<IDENTIFIER>'           ⇒ [<ID:...>]
                    | '(' ')'                ⇒ [] 
                    | '(' Vl ')'             ⇒ [','-node or single <ID>]
        """
        result: List[ASTNode] = []

        # Case: simple identifier
        if self._peek().type == "<IDENTIFIER>":
            tok = self._advance()
            result.append(ASTNode(f"<ID:{tok.content}>"))
            return result

        # Case: '(' ')' or '(' Vl ')'
        if self._peek().content == "(":
            self._match("(")
            # '()' → zero identifiers
            if self._peek().content == ")":
                self._match(")")
                return []  # empty parameter list
            # Otherwise parse Vl_list_inner
            vl_nodes = self.Vl_list_inner()
            self._match(")")
            # If Vl_list_inner returned multiple IDs, wrap them under a comma node
            if len(vl_nodes) > 1:
                comma_node = ASTNode(",")
                for v in vl_nodes:
                    comma_node.add_child(v)
                result.append(comma_node)
            elif len(vl_nodes) == 1:
                result.append(vl_nodes[0])
            # else: no IDs
            return result

        raise SyntaxError("Identifier or '(' expected",
                          self._peek().content, self._peek().line)

    def Vl_list_inner(self) -> List[ASTNode]:
        """
        Parses Vl → '<IDENTIFIER>' (',' '<IDENTIFIER>')*
        Returns a list of ASTNode("<ID:...>").
        """
        first_tok = self._match_type("<IDENTIFIER>")
        var_nodes: List[ASTNode] = [ASTNode(f"<ID:{first_tok.content}>")]
        while self._peek().content == ",":
            self._match(",")
            next_tok = self._match_type("<IDENTIFIER>")
            var_nodes.append(ASTNode(f"<ID:{next_tok.content}>"))
        return var_nodes
