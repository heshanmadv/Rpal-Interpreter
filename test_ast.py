import io
import sys
from src.parser import Parser
from src.rpal_ast import preorder_traversal


def _capture_ast(code: str) -> str:
    buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buf
    try:
        root = Parser(code).parse()
        preorder_traversal(root)
    finally:
        sys.stdout = old_stdout
    return buf.getvalue().rstrip("\n")




def test_Innerproduct1():
    expected = """let
.function_form
..<ID:Innerproduct>
..,
...<ID:S1>
...<ID:S2>
..where
...->
....not
.....&
......gamma
.......<ID:Istuple>
.......<ID:S1>
......gamma
.......<ID:Istuple>
.......<ID:S2>
....<STR:'Args not both tuples'>
....->
.....ne
......gamma
.......<ID:Order>
.......<ID:S1>
......gamma
.......<ID:Order>
.......<ID:S2>
.....<STR:'Args of unequal length'>
.....gamma
......<ID:Partial_sum>
......tau
.......<ID:S1>
.......<ID:S2>
.......gamma
........<ID:Order>
........<ID:S1>
...rec
....function_form
.....<ID:Partial_sum>
.....,
......<ID:A>
......<ID:B>
......<ID:N>
.....->
......eq
.......<ID:N>
.......<INT:0>
......<INT:0>
......+
.......*
........gamma
.........<ID:A>
.........<ID:N>
........gamma
.........<ID:B>
.........<ID:N>
.......gamma
........<ID:Partial_sum>
........tau
.........<ID:A>
.........<ID:B>
.........-
..........<ID:N>
..........<INT:1>
.gamma
..<ID:Print>
..tau
...gamma
....<ID:Innerproduct>
....tau
.....<nil>
.....<nil>
...gamma
....<ID:Innerproduct>
....tau
.....tau
......<INT:1>
......<INT:2>
......<INT:3>
.....tau
......<INT:4>
......<INT:5>
......<INT:6>
...gamma
....<ID:Innerproduct>
....tau
.....tau
......<INT:1>
......<INT:2>
.....tau
......<INT:3>
......<INT:4>
......<INT:5>
...gamma
....<ID:Innerproduct>
....tau
.....<INT:1>
.....tau
......<INT:2>
......<INT:3>
......<INT:4>"""
    with open(r"Tests\Innerproduct1") as f:
        code = f.read()
    actual = _capture_ast(code)
    assert actual == expected, "AST mismatch on Innerproduct1"


def test_Innerproduct2():
    expected = """let
.function_form
..<ID:Innerproduct>
..<ID:S1>
..<ID:S2>
..where
...->
....not
.....&
......gamma
.......<ID:Istuple>
.......<ID:S1>
......gamma
.......<ID:Istuple>
.......<ID:S2>
....<STR:'Args not both tuples'>
....->
.....ne
......gamma
.......<ID:Order>
.......<ID:S1>
......gamma
.......<ID:Order>
.......<ID:S2>
.....<STR:'Args of unequal length'>
.....gamma
......gamma
.......gamma
........<ID:Partial_sum>
........<ID:S1>
.......<ID:S2>
......gamma
.......<ID:Order>
.......<ID:S1>
...rec
....function_form
.....<ID:Partial_sum>
.....<ID:A>
.....<ID:B>
.....<ID:N>
.....->
......eq
.......<ID:N>
.......<INT:0>
......<INT:0>
......+
.......*
........gamma
.........<ID:A>
.........<ID:N>
........gamma
.........<ID:B>
.........<ID:N>
.......gamma
........gamma
.........gamma
..........<ID:Partial_sum>
..........<ID:A>
.........<ID:B>
........-
.........<ID:N>
.........<INT:1>
.gamma
..<ID:Print>
..tau
...gamma
....gamma
.....<ID:Innerproduct>
.....<nil>
....<nil>
...gamma
....gamma
.....<ID:Innerproduct>
.....tau
......<INT:1>
......<INT:2>
......<INT:3>
....tau
.....<INT:4>
.....<INT:5>
.....<INT:6>
...gamma
....gamma
.....<ID:Innerproduct>
.....tau
......<INT:1>
......<INT:2>
....tau
.....<INT:3>
.....<INT:4>
.....<INT:5>
...gamma
....gamma
.....<ID:Innerproduct>
.....<INT:1>
....tau
.....<INT:2>
.....<INT:3>
.....<INT:4>"""
    with open(r"Tests\Innerproduct2") as f:
        code = f.read()
    actual = _capture_ast(code)
    assert actual == expected, "AST mismatch on Innerproduct2"


def test_Treepicture():
    expected = """let
.rec
..function_form
...<ID:TreePicture>
...<ID:T>
...where
....->
.....not
......gamma
.......<ID:Istuple>
.......<ID:T>
.....<STR:'T'>
.....@
......@
.......@
........gamma
.........<ID:ItoS>
.........gamma
..........<ID:Order>
..........<ID:T>
........<ID:Conc>
........<STR:'('>
.......<ID:Conc>
.......gamma
........<ID:TPicture>
........tau
.........<ID:T>
.........gamma
..........<ID:Order>
..........<ID:T>
......<ID:Conc>
......<STR:')'>
....rec
.....function_form
......<ID:TPicture>
......,
.......<ID:T>
.......<ID:N>
......->
.......eq
........<ID:N>
........<INT:0>
.......<STR:''>
.......->
........eq
.........<ID:N>
.........<INT:1>
........gamma
.........<ID:TreePicture>
.........gamma
..........<ID:T>
..........<ID:N>
........@
.........@
..........gamma
...........<ID:TPicture>
...........tau
............<ID:T>
............-
.............<ID:N>
.............<INT:1>
..........<ID:Conc>
..........<STR:','>
.........<ID:Conc>
.........gamma
..........<ID:TreePicture>
..........gamma
...........<ID:T>
...........<ID:N>
.gamma
..<ID:Print>
..tau
...gamma
....<ID:TreePicture>
....<nil>
...gamma
....<ID:TreePicture>
....aug
.....<nil>
.....<true>
...gamma
....<ID:TreePicture>
....tau
.....tau
......<INT:1>
......tau
.......<INT:2>
.......<INT:3>
.......<INT:4>
......<INT:5>
.....tau
......<INT:6>
......<STR:'7'>
.....tau
......<INT:8>
......<INT:9>
......<nil>
.....aug
......<nil>
......<INT:10>"""
    with open(r"Tests\Treepicture") as f:
        code = f.read()
    actual = _capture_ast(code)
    assert actual == expected, "AST mismatch on Treepicture"


def test_add():
    expected = """let
.function_form
..<ID:Sum>
..<ID:A>
..where
...gamma
....<ID:Psum>
....tau
.....<ID:A>
.....gamma
......<ID:Order>
......<ID:A>
...rec
....function_form
.....<ID:Psum>
.....,
......<ID:T>
......<ID:N>
.....->
......eq
.......<ID:N>
.......<INT:0>
......<INT:0>
......+
.......gamma
........<ID:Psum>
........tau
.........<ID:T>
.........-
..........<ID:N>
..........<INT:1>
.......gamma
........<ID:T>
........<ID:N>
.gamma
..<ID:Print>
..gamma
...<ID:Sum>
...tau
....<INT:1>
....<INT:2>
....<INT:3>
....<INT:4>
....<INT:5>"""
    with open(r"Tests\add") as f:
        code = f.read()
    actual = _capture_ast(code)
    assert actual == expected, "AST mismatch on add"


def test_unique():
    expected = """let
.function_form
..<ID:Is_Element>
..<ID:Number>
..<ID:Tuple>
..where
...gamma
....gamma
.....gamma
......<ID:Rec_Is_Element>
......<ID:Number>
.....<ID:Tuple>
....gamma
.....<ID:Order>
.....<ID:Tuple>
...rec
....function_form
.....<ID:Rec_Is_Element>
.....<ID:Number>
.....<ID:Tuple>
.....<ID:M>
.....->
......eq
.......<ID:M>
.......<INT:0>
......<false>
......->
.......eq
........gamma
.........<ID:Tuple>
.........<ID:M>
........<ID:Number>
.......<true>
.......gamma
........gamma
.........gamma
..........<ID:Rec_Is_Element>
..........<ID:Number>
.........<ID:Tuple>
........-
.........<ID:M>
.........<INT:1>
.let
..rec
...function_form
....<ID:Rec_F>
....<ID:Tuple>
....<ID:Index>
....->
.....eq
......<ID:Index>
......<INT:0>
.....<nil>
.....let
......=
.......<ID:Result>
.......gamma
........gamma
.........<ID:Rec_F>
.........<ID:Tuple>
........-
.........<ID:Index>
.........<INT:1>
......->
.......gamma
........gamma
.........<ID:Is_Element>
.........gamma
..........<ID:Tuple>
..........<ID:Index>
........<ID:Result>
.......<ID:Result>
.......aug
........<ID:Result>
........gamma
.........<ID:Tuple>
.........<ID:Index>
..let
...function_form
....<ID:F>
....<ID:Tuple>
....gamma
.....gamma
......<ID:Rec_F>
......<ID:Tuple>
.....gamma
......<ID:Order>
......<ID:Tuple>
...gamma
....<ID:Print>
....gamma
.....<ID:F>
.....tau
......<INT:1>
......<INT:2>
......<INT:3>
......<INT:2>
......<INT:4>
......<INT:5>
......<INT:4>"""
    with open(r"Tests\unique") as f:
        code = f.read()
    actual = _capture_ast(code)
    assert actual == expected, "AST mismatch on unique"


def test_conc1():
    expected = """let
.=
..<ID:Message>
..<STR:'HELLO'>
.gamma
..<ID:Print>
..tau
...gamma
....gamma
.....<ID:Conc>
.....<ID:Message>
....<STR:'!'>
...<STR:'dflsdfiuh'>
...<STR:'dkgh'>"""
    with open(r"Tests\conc1") as f:
        code = f.read()
    actual = _capture_ast(code)
    assert actual == expected, "AST mismatch on conc1"


def test_conc2():
    expected = """let
.function_form
..<ID:Conc>
..<ID:x>
..<ID:y>
..gamma
...gamma
....<ID:Conc>
....<ID:x>
...<ID:y>
.let
..and
...=
....<ID:S>
....<STR:'CIS'>
...=
....<ID:T>
....<STR:'104B'>
...=
....<ID:Mark>
....gamma
.....<ID:Conc>
.....<STR:'CIS'>
..gamma
...<ID:Print>
...tau
....gamma
.....gamma
......<ID:Conc>
......<ID:S>
.....<ID:T>
....@
.....<ID:S>
.....<ID:Conc>
.....<ID:T>
....gamma
.....<ID:Mark>
.....<ID:T>"""
    with open(r"Tests\conc2") as f:
        code = f.read()
    actual = _capture_ast(code)
    assert actual == expected, "AST mismatch on conc2"





def test_func1():
    expected = """gamma
.<ID:Print>
.let
..function_form
...<ID:f>
...<ID:x>
...<ID:y>
...let
....function_form
.....<ID:g>
.....<ID:x>
.....<ID:y>
.....let
......function_form
.......<ID:h>
.......<ID:x>
.......<ID:y>
.......gamma
........gamma
.........<ID:x>
.........<ID:y>
........<ID:x>
......<ID:h>
....<ID:g>
..<ID:f>"""
    with open(r"Tests\func1") as f:
        code = f.read()
    actual = _capture_ast(code)
    assert actual == expected, "AST mismatch on func1"


def test_func2():
    expected = """gamma
.<ID:Print>
.where
..+
...<ID:x>
...<INT:1>
..=
...<ID:x>
...where
....+
.....<ID:y>
.....<INT:3>
....=
.....<ID:y>
.....where
......+
.......<ID:z>
.......<INT:4>
......=
.......<ID:z>
.......<INT:7>"""
    with open(r"Tests\func2") as f:
        code = f.read()
    actual = _capture_ast(code)
    assert actual == expected, "AST mismatch on func2"




def test_adder():
    expected = """let
.function_form
..<ID:add>
..<ID:n>
..where
...gamma
....gamma
.....<ID:radd>
.....<INT:0>
....<ID:n>
...rec
....function_form
.....<ID:radd>
.....<ID:r>
.....<ID:n>
.....->
......eq
.......<ID:n>
.......<INT:0>
......<ID:r>
......gamma
.......<ID:radd>
.......+
........<ID:r>
........<ID:n>
.gamma
..<ID:print>
..gamma
...gamma
....gamma
.....gamma
......<ID:add>
......<INT:2>
.....<INT:3>
....<INT:4>
...<INT:0>"""
    with open(r"Tests\adder") as f:
        code = f.read()
    actual = _capture_ast(code)
    assert actual == expected, "AST mismatch on adder"


def test_div():
    expected = """gamma
.lambda
..<ID:a>
..gamma
...<ID:Print>
.../
....<ID:a>
....<INT:3>
.<INT:6>"""
    with open(r"Tests\div") as f:
        code = f.read()
    actual = _capture_ast(code)
    assert actual == expected, "AST mismatch on div"


def test_sample():
    expected = """let
.=
..<ID:a>
..<INT:1>
.let
..=
...<ID:b>
...<ID:a>
..<ID:b>"""
    with open(r"Tests\sample") as f:
        code = f.read()
    actual = _capture_ast(code)
    assert actual == expected, "AST mismatch on sample"


def test_fn1():
    expected = """gamma
.<ID:Print>
.gamma
..lambda
...<ID:f>
...gamma
....<ID:f>
....<INT:2>
..lambda
...<ID:x>
...->
....eq
.....<ID:x>
.....<INT:1>
....<INT:1>
....+
.....<ID:x>
.....<INT:2>"""
    with open(r"Tests\fn1") as f:
        code = f.read()
    actual = _capture_ast(code)
    assert actual == expected, "AST mismatch on fn1"


def test_fn2():
    expected = """gamma
.<ID:Print>
.gamma
..lambda
...<ID:f>
...gamma
....<ID:f>
....<STR:'first letter missing in this sentence?'>
..lambda
...<ID:x>
...gamma
....<ID:Stern>
....<ID:x>"""
    with open(r"Tests\fn2") as f:
        code = f.read()
    actual = _capture_ast(code)
    assert actual == expected, "AST mismatch on fn2"


def test_fn3():
    expected = """gamma
.<ID:Print>
.gamma
..lambda
...<ID:x>
...+
....<ID:x>
....<INT:1>
..gamma
...lambda
....<ID:y>
....+
.....<ID:y>
.....<INT:3>
...gamma
....lambda
.....<ID:z>
.....+
......<ID:z>
......<INT:4>
....<INT:7>"""
    with open(r"Tests\fn3") as f:
        code = f.read()
    actual = _capture_ast(code)
    assert actual == expected, "AST mismatch on fn3"
