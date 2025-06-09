import io
import sys
from src.parser import Parser
from src.standardizer import make_standardized_tree
from src.rpal_ast import preorder_traversal


def _capture_st_(code: str) -> str:
    buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buf
    try:
        ast_root = Parser(code).parse()
        st_root = make_standardized_tree(ast_root)
        preorder_traversal(st_root)
    finally:
        sys.stdout = old_stdout
    return buf.getvalue().rstrip("\n")




def test_Innerprod():
    expected = """gamma
.lambda
..<ID:Innerproduct>
..gamma
...<ID:Print>
...tau
....gamma
.....<ID:Innerproduct>
.....tau
......<nil>
......<nil>
....gamma
.....<ID:Innerproduct>
.....tau
......tau
.......<INT:1>
.......<INT:2>
.......<INT:3>
......tau
.......<INT:4>
.......<INT:5>
.......<INT:6>
....gamma
.....<ID:Innerproduct>
.....tau
......tau
.......<INT:1>
.......<INT:2>
......tau
.......<INT:3>
.......<INT:4>
.......<INT:5>
....gamma
.....<ID:Innerproduct>
.....tau
......<INT:1>
......tau
.......<INT:2>
.......<INT:3>
.......<INT:4>
.lambda
..,
...<ID:S1>
...<ID:S2>
..gamma
...lambda
....<ID:Partial_sum>
....->
.....not
......&
.......gamma
........<ID:Istuple>
........<ID:S1>
.......gamma
........<ID:Istuple>
........<ID:S2>
.....<STR:'Args not both tuples'>
.....->
......ne
.......gamma
........<ID:Order>
........<ID:S1>
.......gamma
........<ID:Order>
........<ID:S2>
......<STR:'Args of unequal length'>
......gamma
.......<ID:Partial_sum>
.......tau
........<ID:S1>
........<ID:S2>
........gamma
.........<ID:Order>
.........<ID:S1>
...gamma
....<Y*>
....lambda
.....<ID:Partial_sum>
.....lambda
......,
.......<ID:A>
.......<ID:B>
.......<ID:N>
......->
.......eq
........<ID:N>
........<INT:0>
.......<INT:0>
.......+
........*
.........gamma
..........<ID:A>
..........<ID:N>
.........gamma
..........<ID:B>
..........<ID:N>
........gamma
.........<ID:Partial_sum>
.........tau
..........<ID:A>
..........<ID:B>
..........-
...........<ID:N>
...........<INT:1>"""

    with open(r"Tests\Innerprod") as f:
        code = f.read()
    actual = _capture_st_(code)
    assert actual == expected, "AST mismatch on Innerprod"


def test_Innerprod2():
    expected = """gamma
.lambda
..<ID:Innerproduct>
..gamma
...<ID:Print>
...tau
....gamma
.....gamma
......<ID:Innerproduct>
......<nil>
.....<nil>
....gamma
.....gamma
......<ID:Innerproduct>
......tau
.......<INT:1>
.......<INT:2>
.......<INT:3>
.....tau
......<INT:4>
......<INT:5>
......<INT:6>
....gamma
.....gamma
......<ID:Innerproduct>
......tau
.......<INT:1>
.......<INT:2>
.....tau
......<INT:3>
......<INT:4>
......<INT:5>
....gamma
.....gamma
......<ID:Innerproduct>
......<INT:1>
.....tau
......<INT:2>
......<INT:3>
......<INT:4>
.lambda
..<ID:S1>
..lambda
...<ID:S2>
...gamma
....lambda
.....<ID:Partial_sum>
.....->
......not
.......&
........gamma
.........<ID:Istuple>
.........<ID:S1>
........gamma
.........<ID:Istuple>
.........<ID:S2>
......<STR:'Args not both tuples'>
......->
.......ne
........gamma
.........<ID:Order>
.........<ID:S1>
........gamma
.........<ID:Order>
.........<ID:S2>
.......<STR:'Args of unequal length'>
.......gamma
........gamma
.........gamma
..........<ID:Partial_sum>
..........<ID:S1>
.........<ID:S2>
........gamma
.........<ID:Order>
.........<ID:S1>
....gamma
.....<Y*>
.....lambda
......<ID:Partial_sum>
......lambda
.......<ID:A>
.......lambda
........<ID:B>
........lambda
.........<ID:N>
.........->
..........eq
...........<ID:N>
...........<INT:0>
..........<INT:0>
..........+
...........*
............gamma
.............<ID:A>
.............<ID:N>
............gamma
.............<ID:B>
.............<ID:N>
...........gamma
............gamma
.............gamma
..............<ID:Partial_sum>
..............<ID:A>
.............<ID:B>
............-
.............<ID:N>
.............<INT:1>"""

    with open(r"Tests\Innerprod2") as f:
        code = f.read()
    actual = _capture_st_(code)
    assert actual == expected, "AST mismatch on Innerprod2"


def test_Treepicture():
    expected = """gamma
.lambda
..<ID:TreePicture>
..gamma
...<ID:Print>
...tau
....gamma
.....<ID:TreePicture>
.....<nil>
....gamma
.....<ID:TreePicture>
.....aug
......<nil>
......<true>
....gamma
.....<ID:TreePicture>
.....tau
......tau
.......<INT:1>
.......tau
........<INT:2>
........<INT:3>
........<INT:4>
.......<INT:5>
......tau
.......<INT:6>
.......<STR:'7'>
......tau
.......<INT:8>
.......<INT:9>
.......<nil>
......aug
.......<nil>
.......<INT:10>
.gamma
..<Y*>
..lambda
...<ID:TreePicture>
...lambda
....<ID:T>
....gamma
.....lambda
......<ID:TPicture>
......->
.......not
........gamma
.........<ID:Istuple>
.........<ID:T>
.......<STR:'T'>
.......gamma
........gamma
.........<ID:Conc>
.........gamma
..........gamma
...........<ID:Conc>
...........gamma
............gamma
.............<ID:Conc>
.............gamma
..............<ID:ItoS>
..............gamma
...............<ID:Order>
...............<ID:T>
............<STR:'('>
..........gamma
...........<ID:TPicture>
...........tau
............<ID:T>
............gamma
.............<ID:Order>
.............<ID:T>
........<STR:')'>
.....gamma
......<Y*>
......lambda
.......<ID:TPicture>
.......lambda
........,
.........<ID:T>
.........<ID:N>
........->
.........eq
..........<ID:N>
..........<INT:0>
.........<STR:''>
.........->
..........eq
...........<ID:N>
...........<INT:1>
..........gamma
...........<ID:TreePicture>
...........gamma
............<ID:T>
............<ID:N>
..........gamma
...........gamma
............<ID:Conc>
............gamma
.............gamma
..............<ID:Conc>
..............gamma
...............<ID:TPicture>
...............tau
................<ID:T>
................-
.................<ID:N>
.................<INT:1>
.............<STR:','>
...........gamma
............<ID:TreePicture>
............gamma
.............<ID:T>
.............<ID:N>"""

    with open(r"Tests\Treepicture") as f:
        code = f.read()
    actual = _capture_st_(code)
    assert actual == expected, "AST mismatch on Treepicture"


def test_add():
    expected = """gamma
.lambda
..<ID:Sum>
..gamma
...<ID:Print>
...gamma
....<ID:Sum>
....tau
.....<INT:1>
.....<INT:2>
.....<INT:3>
.....<INT:4>
.....<INT:5>
.lambda
..<ID:A>
..gamma
...lambda
....<ID:Psum>
....gamma
.....<ID:Psum>
.....tau
......<ID:A>
......gamma
.......<ID:Order>
.......<ID:A>
...gamma
....<Y*>
....lambda
.....<ID:Psum>
.....lambda
......,
.......<ID:T>
.......<ID:N>
......->
.......eq
........<ID:N>
........<INT:0>
.......<INT:0>
.......+
........gamma
.........<ID:Psum>
.........tau
..........<ID:T>
..........-
...........<ID:N>
...........<INT:1>
........gamma
.........<ID:T>
.........<ID:N>"""

    with open(r"Tests\add") as f:
        code = f.read()
    actual = _capture_st_(code)
    assert actual == expected, "AST mismatch on add"


def test_unique():
    expected = """gamma
.lambda
..<ID:Is_Element>
..gamma
...lambda
....<ID:Rec_F>
....gamma
.....lambda
......<ID:F>
......gamma
.......<ID:Print>
.......gamma
........<ID:F>
........tau
.........<INT:1>
.........<INT:2>
.........<INT:3>
.........<INT:2>
.........<INT:4>
.........<INT:5>
.........<INT:4>
.....lambda
......<ID:Tuple>
......gamma
.......gamma
........<ID:Rec_F>
........<ID:Tuple>
.......gamma
........<ID:Order>
........<ID:Tuple>
...gamma
....<Y*>
....lambda
.....<ID:Rec_F>
.....lambda
......<ID:Tuple>
......lambda
.......<ID:Index>
.......->
........eq
.........<ID:Index>
.........<INT:0>
........<nil>
........gamma
.........lambda
..........<ID:Result>
..........->
...........gamma
............gamma
.............<ID:Is_Element>
.............gamma
..............<ID:Tuple>
..............<ID:Index>
............<ID:Result>
...........<ID:Result>
...........aug
............<ID:Result>
............gamma
.............<ID:Tuple>
.............<ID:Index>
.........gamma
..........gamma
...........<ID:Rec_F>
...........<ID:Tuple>
..........-
...........<ID:Index>
...........<INT:1>
.lambda
..<ID:Number>
..lambda
...<ID:Tuple>
...gamma
....lambda
.....<ID:Rec_Is_Element>
.....gamma
......gamma
.......gamma
........<ID:Rec_Is_Element>
........<ID:Number>
.......<ID:Tuple>
......gamma
.......<ID:Order>
.......<ID:Tuple>
....gamma
.....<Y*>
.....lambda
......<ID:Rec_Is_Element>
......lambda
.......<ID:Number>
.......lambda
........<ID:Tuple>
........lambda
.........<ID:M>
.........->
..........eq
...........<ID:M>
...........<INT:0>
..........<false>
..........->
...........eq
............gamma
.............<ID:Tuple>
.............<ID:M>
............<ID:Number>
...........<true>
...........gamma
............gamma
.............gamma
..............<ID:Rec_Is_Element>
..............<ID:Number>
.............<ID:Tuple>
............-
.............<ID:M>
.............<INT:1>"""

    with open(r"Tests\unique") as f:
        code = f.read()
    actual = _capture_st_(code)
    assert actual == expected, "AST mismatch on unique"


def test_conc1():
    expected = """gamma
.lambda
..<ID:Message>
..gamma
...<ID:Print>
...tau
....gamma
.....gamma
......<ID:Conc>
......<ID:Message>
.....<STR:'!'>
....<STR:'dflsdfiuh'>
....<STR:'dkgh'>
.<STR:'HELLO'>"""

    with open(r"Tests\conc1") as f:
        code = f.read()
    actual = _capture_st_(code)
    assert actual == expected, "AST mismatch on conc1"


def test_conc2():
    expected = """gamma
.lambda
..<ID:Conc>
..gamma
...lambda
....,
.....<ID:S>
.....<ID:T>
.....<ID:Mark>
....gamma
.....<ID:Print>
.....tau
......gamma
.......gamma
........<ID:Conc>
........<ID:S>
.......<ID:T>
......gamma
.......gamma
........<ID:Conc>
........<ID:S>
.......<ID:T>
......gamma
.......<ID:Mark>
.......<ID:T>
...tau
....<STR:'CIS'>
....<STR:'104B'>
....gamma
.....<ID:Conc>
.....<STR:'CIS'>
.lambda
..<ID:x>
..lambda
...<ID:y>
...gamma
....gamma
.....<ID:Conc>
.....<ID:x>
....<ID:y>"""

    with open(r"Tests\conc2") as f:
        code = f.read()
    actual = _capture_st_(code)
    assert actual == expected, "AST mismatch on conc2"


def test_conc3():
    expected = """gamma
.lambda
..,
...<ID:S>
...<ID:T>
..gamma
...<ID:Print>
...gamma
....gamma
.....<ID:Conc>
.....<ID:S>
....<ID:T>
.tau
..<STR:'CIS'>
..<STR:'104B'>"""

    with open(r"Tests\conc3") as f:
        code = f.read()
    actual = _capture_st_(code)
    assert actual == expected, "AST mismatch on conc3"


def test_defns_1():
    expected = """gamma
.<ID:Print>
.gamma
..lambda
...<ID:f>
...<ID:f>
..lambda
...<ID:x>
...lambda
....<ID:y>
....gamma
.....lambda
......<ID:g>
......<ID:g>
.....lambda
......<ID:x>
......lambda
.......<ID:y>
.......gamma
........lambda
.........<ID:h>
.........<ID:h>
........lambda
.........<ID:x>
.........lambda
..........<ID:y>
..........gamma
...........gamma
............<ID:x>
............<ID:y>
...........<ID:x>"""

    with open(r"Tests\defns.1") as f:
        code = f.read()
    actual = _capture_st_(code)
    assert actual == expected, "AST mismatch on defns.1"


def test_defns_2():
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

    with open(r"Tests\defns.2") as f:
        code = f.read()
    actual = _capture_st_(code)
    assert actual == expected, "AST mismatch on defns.2"


def test_defns_3():
    expected = """gamma
.lambda
..<ID:f>
..gamma
...<ID:f>
...tau
....<INT:1>
....<INT:2>
....<INT:3>
.lambda
..,
...<ID:x>
...<ID:y>
...<ID:z>
..+
...+
....<ID:x>
....<ID:y>
...<ID:z>"""

    with open(r"Tests\defns.3") as f:
        code = f.read()
    actual = _capture_st_(code)
    assert actual == expected, "AST mismatch on defns.3"


def test_dist():
    expected = """gamma
.lambda
..<ID:add>
..gamma
...<ID:print>
...gamma
....gamma
.....gamma
......gamma
.......<ID:add>
.......<INT:2>
......<INT:3>
.....<INT:4>
....<INT:0>
.lambda
..<ID:n>
..gamma
...lambda
....<ID:radd>
....gamma
.....gamma
......<ID:radd>
......<INT:0>
.....<ID:n>
...gamma
....<Y*>
....lambda
.....<ID:radd>
.....lambda
......<ID:r>
......lambda
.......<ID:n>
.......->
........eq
.........<ID:n>
.........<INT:0>
........<ID:r>
........gamma
.........<ID:radd>
.........+
..........<ID:r>
..........<ID:n>"""

    with open(r"Tests\dist") as f:
        code = f.read()
    actual = _capture_st_(code)
    assert actual == expected, "AST mismatch on dist"


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
    actual = _capture_st_(code)
    assert actual == expected, "AST mismatch on div"


def test_envlist():
    expected = """gamma
.lambda
..<ID:a>
..gamma
...lambda
....<ID:b>
....<ID:b>
...<ID:a>
.<INT:1>"""

    with open(r"Tests\envlist") as f:
        code = f.read()
    actual = _capture_st_(code)
    assert actual == expected, "AST mismatch on envlist"


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
    actual = _capture_st_(code)
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
    actual = _capture_st_(code)
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
    actual = _capture_st_(code)
    assert actual == expected, "AST mismatch on fn3"
