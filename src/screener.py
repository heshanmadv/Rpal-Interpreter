from typing import List, Tuple, Optional
from src.lexer import Lexer
from src.rpal_token import Token, TokenType
from src.errors import LexicalError


class Screener:
    """
    Takes a list of Tokens, removes DELETE tokens, turns identifiers into KEYWORDs when needed,
    and reports any invalid tokens.
    """

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens: List[Token] = tokens

    def screen(self) -> Tuple[List[Token], bool, Optional[Token]]:
        """
        Returns (filtered_tokens, has_invalid, first_invalid_token).
        Any Token of type TokenType.INVALID triggers has_invalid=True.
        """
        filtered: List[Token] = []
        first_invalid: Optional[Token] = None

        for tok in self.tokens:
            if tok.type == TokenType.INVALID:
                if first_invalid is None:
                    first_invalid = tok
                continue
            if tok.type == TokenType.DELETE:
                continue
            # Any identifier matching a keyword list should be made a KEYWORD
            if tok.type == TokenType.IDENTIFIER and tok.content in Lexer.KEYWORDS:
                tok.make_keyword()
            filtered.append(tok)

        if first_invalid:
            return (filtered, True, first_invalid)
        return (filtered, False, None)
