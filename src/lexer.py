from __future__ import annotations
from typing import List, Tuple
from src.rpal_token import Token, TokenType
from src.errors import TokenizationError


class Lexer:
    """
    Turns a raw string (list of characters) into a list of Token objects.
    """

    KEYWORDS: List[str] = [
        "let", "in", "where", "rec", "fn", "aug", "or", "not",
        "gr", "ge", "ls", "le", "eq", "ne", "true", "false",
        "nil", "dummy", "within", "and"
    ]

    SIMPLE_OPERATORS: List[str] = [
        "+", "-", "*", "/", "**", "=", "->", "@", "&", ":", ";", ",", ".",
        "(", ")", "[", "]"
    ]

    COMPARISON_OPERATORS: List[str] = ["gr", "ge", "ls", "le", "eq", "ne"]

    def __init__(self, source: str) -> None:
        self.source: str = source
        self.position: int = 0
        self.line: int = 1
        self.length: int = len(source)
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        """
        Main entry point: run through source, produce a list of Token objects.
        Comments and whitespace become TokenType.DELETE or are dropped.
        """
        while not self._at_end():
            ch = self._peek()
            if ch.isspace():
                self._consume_whitespace()
            elif ch == "/" and self._peek_next() == "/":
                self._consume_comment()
            elif ch.isalpha():
                self._consume_identifier_or_keyword()
            elif ch.isdigit():
                self._consume_number()
            elif ch == "'":
                self._consume_string()
            else:
                self._consume_operator_or_punct()
        # Mark first/last tokens if any
        if self.tokens:
            self.tokens[0].mark_first()
            self.tokens[-1].mark_last()
        return self.tokens

    def _at_end(self) -> bool:
        return self.position >= self.length

    def _peek(self) -> str:
        return self.source[self.position]

    def _peek_next(self) -> str:
        if self.position + 1 < self.length:
            return self.source[self.position + 1]
        return "\0"

    def _advance(self) -> str:
        ch = self.source[self.position]
        self.position += 1
        if ch == "\n":
            self.line += 1
        return ch

    def _add_token(self, content: str, tok_type: str) -> None:
        self.tokens.append(Token(content, tok_type, self.line))

    def _consume_whitespace(self) -> None:
        while not self._at_end() and self._peek().isspace():
            self._advance()

    def _consume_comment(self) -> None:
        # Skip '//' and rest of line
        self._advance()  # '/'
        self._advance()  # second '/'
        while not self._at_end() and self._peek() != "\n":
            self._advance()
        # We leave the newline in place so that line count increments
        # in _advance() when next consumed.

    def _consume_identifier_or_keyword(self) -> None:
        start_pos = self.position
        while not self._at_end() and (self._peek().isalnum() or self._peek() == "_"):
            self._advance()
        content = self.source[start_pos: self.position]
        if content in Lexer.KEYWORDS:
            self._add_token(content, TokenType.KEYWORD)
        else:
            self._add_token(content, TokenType.IDENTIFIER)

    def _consume_number(self) -> None:
        start_pos = self.position
        while not self._at_end() and self._peek().isdigit():
            self._advance()
        # If next char is letter, it's invalid (e.g., "123abc")
        if not self._at_end() and self._peek().isalpha():
            invalid = self.source[start_pos: self.position + 1]
            raise TokenizationError(invalid, self.line)
        content = self.source[start_pos: self.position]
        self._add_token(content, TokenType.INTEGER)

    def _consume_string(self) -> None:
        # Opening quote
        self._advance()  # consume "'"
        start_pos = self.position
        while not self._at_end() and self._peek() != "'":
            self._advance()
        if self._at_end():
            raise TokenizationError("Unterminated string literal", self.line)
        # Closing quote
        self._advance()
        content = self.source[start_pos - 1: self.position]  # include quotes
        self._add_token(content, TokenType.STRING)

    def _consume_operator_or_punct(self) -> None:
        ch = self._peek()
        two_char = ch + self._peek_next()
        if two_char in ("**", "->"):
            self._advance()
            self._advance()
            self._add_token(two_char, TokenType.OPERATOR)
            return
        if ch in "+-*/=@&|:,.;()[]":
            self._advance()
            self._add_token(
                ch, TokenType.OPERATOR if ch not in "()[],.:;@&" else ch)
            return
        # Potential multi‐letter operator like "gr", "ge", etc.
        if self._peek().isalpha():
            start_pos = self.position
            while not self._at_end() and self._peek().isalpha():
                self._advance()
            content = self.source[start_pos: self.position]
            if content in Lexer.COMPARISON_OPERATORS:
                self._add_token(content, TokenType.OPERATOR)
            else:
                raise TokenizationError(content, self.line)
            return
        # If we reach here, it's an unexpected character
        invalid_char = self._advance()
        raise TokenizationError(invalid_char, self.line)
