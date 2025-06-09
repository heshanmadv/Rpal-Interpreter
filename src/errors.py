class RPALException(Exception):
    """Base class for all RPAL‐related errors."""
    pass


class LexicalError(RPALException):
    def __init__(self, message: str, line: int) -> None:
        super().__init__(f"[Lexical Error on line {line}]: {message}")


class SyntaxError(RPALException):
    def __init__(self, expected: str, got: str, line: int) -> None:
        super().__init__(
            f"[Syntax Error on line {line}]: Expected '{expected}', but got '{got}'")


class TokenizationError(RPALException):
    def __init__(self, content: str, line: int) -> None:
        super().__init__(
            f"[Tokenization Error on line {line}]: Invalid token '{content}'")
