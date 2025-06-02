from __future__ import annotations
from typing import Final


class TokenType:
    IDENTIFIER: Final[str] = "<IDENTIFIER>"
    INTEGER: Final[str] = "<INTEGER>"
    STRING: Final[str] = "<STRING>"
    OPERATOR: Final[str] = "<OPERATOR>"
    KEYWORD: Final[str] = "<KEYWORD>"
    DELETE: Final[str] = "<DELETE>"
    INVALID: Final[str] = "<INVALID>"


class Token:
    """
    Represents a single lexical token.
    """

    __slots__ = ("content", "type", "line", "is_first_token", "is_last_token")

    def __init__(self, content: str, tok_type: str, line: int) -> None:
        self.content: str = content
        self.type: str = tok_type
        self.line: int = line
        self.is_first_token: bool = False
        self.is_last_token: bool = False

    def __str__(self) -> str:
        return f"{self.content} : {self.type}"

    def make_keyword(self) -> None:
        self.type = TokenType.KEYWORD

    def mark_first(self) -> None:
        self.is_first_token = True

    def mark_last(self) -> None:
        self.is_last_token = True
