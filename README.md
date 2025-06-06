# RPAL Interpreter

This is an interpreter for the RPAL (Right-reference Pure Applicative Language), implemented as the final project for CS3513 - Programming Languages (Semester 4). The interpreter includes a full lexical analyzer, parser, AST and ST generator, and an evaluator via a CSE (Control Stack Environment) machine.

---

## Features

- Lexical analysis (tokenization)
- Abstract Syntax Tree (AST) construction
- Standardized Tree (ST) transformation
- CSE Machine execution for evaluation
- Matches the behavior of `rpal.exe`

---

## Project Structure

```bash
├── myrpal.py               # Main entry point
├── src/
│   ├── parser.py           # Recursive-descent parser
│   ├── lexer.py            # Lexical analyzer
│   ├── rpal_ast.py         # AST data structures and traversal
│   ├── standardizer.py     # AST to ST conversion logic
│   ├── csemachine.py       # CSE machine evaluator
│   ├── rpal_token.py       # Token and TokenType definitions
│   ├── screener.py         # Token cleanup and validation
│   ├── structures.py       # CSE helper structures (Lambda, Delta, Tau, etc.)
│   └── errors.py           # Error handling (lexical, syntax, tokenization)
├── test_ast.py             # Pytest suite for AST validation
├── test_st.py              # Pytest suite for ST validation
├── Tests/                  # RPAL test programs
```

---

## 💾 Usage

Run the interpreter from the command line:

```bash
python .\myrpal.py [options] filename
```

### Options:

- `-l` : Print the source code from the file
- `-ast` : Print the Abstract Syntax Tree (AST)
- `-st` : Print the Standardized Tree (ST)
- No flags : Run the program and evaluate it using the CSE machine

### Example:

```bash
python .\myrpal.py -ast -st Tests/8-t2
```

---

## Running Tests

The project uses `pytest` for testing the correctness of AST and ST outputs against expected results.

### Step 1: Install dependencies

```bash
pip install pytest
```

### Step 2: Run all tests

From the root directory:

```bash
pytest test_ast.py
pytest test_st.py
```

Or run both together:

```bash
pytest
```

---

## Test File Convention

Each test case compares the interpreter's output with the expected output stored as strings. Input RPAL source code files are stored in the `Tests/` folder and used in:

- `test_ast.py` → checks correctness of AST generation
- `test_st.py` → checks correctness of ST standardization

---

## Authors

This project was developed as part of the CS3513 module at the University of Moratuwa.

---
