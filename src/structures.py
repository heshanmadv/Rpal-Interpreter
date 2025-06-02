class Lambda:
    """
    Represents a lambda instruction in the control structure.
    Fields:
      - number: unique index for this function
      - bounded_variable: comma-separated string of formal parameter names
      - environment: index of the environment in which this lambda was created
    """

    def __init__(self, number: int) -> None:
        self.number: int = number
        self.bounded_variable: str = ""
        self.environment: int = 0        # environment index

    def __repr__(self) -> str:
        return f"Λ({self.number}, vars={self.bounded_variable}, env=e_{self.environment})"


class Delta:
    """
    Represents a delta (guard) instruction in the control structure.
    Fields:
      - number: unique index for this guard
    """

    def __init__(self, number: int) -> None:
        self.number: int = number

    def __repr__(self) -> str:
        return f"Δ({self.number})"


class Tau:
    """
    Represents a tuple-construction instruction in the control structure.
    Fields:
      - number: the arity of the tuple (how many elements to pop)
    """

    def __init__(self, number: int) -> None:
        self.number: int = number

    def __repr__(self) -> str:
        return f"τ({self.number})"


class Eta:
    """
    Represents an Eta (fixed-point) instruction in the control structure,
    used for Y*-recursion.
    Fields:
      - number: the index of the original lambda to re-create
      - bounded_variable: copied from the original Lambda
      - environment: copied from the original Lambda
    """

    def __init__(self, number: int) -> None:
        self.number: int = number
        self.bounded_variable: str = ""
        self.environment: int = 0

    def __repr__(self) -> str:
        return f"η({self.number}, vars={self.bounded_variable}, env=e_{self.environment})"
