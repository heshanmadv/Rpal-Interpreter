import sys
from typing import List
from src.parser import Parser
from src.rpal_ast import preorder_traversal, ASTNode
from src.standardizer import standardize, make_standardized_tree
from src.csemachine import get_result
from src.lexer import Lexer
from src.errors import RPALException

USAGE = (
    "Usage:\n"
    "  python main.py [-l] [-ast] [-st] filename\n\n"
    "  -l       : List the source file verbatim\n"
    "  -ast     : Print the Abstract Syntax Tree (AST)\n"
    "  -st      : Print the Standardized Tree (ST)\n"
    "  filename : Path to the RPAL source file"
)


def read_file(path: str) -> str:
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {path}")
        sys.exit(1)


def main(argv: List[str]) -> None:
    if len(argv) < 2:
        print(USAGE)
        sys.exit(1)

    # Exactly one filename at the end
    switches = argv[1:-1]
    filename = argv[-1]
    source_code = read_file(filename)

    try:
        if not switches:
            # No flags → just run it
            result = get_result(source_code)
            if result is not None:
                print(result)
            return

        if any(flag not in ("-l", "-ast", "-st") for flag in switches):
            print(USAGE)
            sys.exit(1)

        # 1. -l : list source
        if "-l" in switches:
            print(source_code)
            print()

        # 2. -ast : print AST
        if "-ast" in switches:
            parser = Parser(source_code)
            ast_root: ASTNode = parser.parse()
            preorder_traversal(ast_root)
            print()

            # If -st is also present, immediately print ST on the same AST
            if "-st" in switches:
                st_root = make_standardized_tree(ast_root)
                preorder_traversal(st_root)
                print()
                return

        # 3. -st (alone)
        if "-st" in switches and "-ast" not in switches:
            st_root = standardize(source_code)
            preorder_traversal(st_root)
            print()
            return

    except RPALException as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
