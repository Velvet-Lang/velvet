import pytest
from velvet_parser import VelvetParser
from velvet_ast import *

@pytest.fixture
def parser():
    return VelvetParser()

def test_parse_var(parser):
    ast = parser.parse("~x: map<int,str> = {};")
    assert isinstance(ast.nodes[0], VarNode)
    assert ast.nodes[0].type.base == 'map'
    assert ast.nodes[0].type.key.base == 'int'
    assert ast.nodes[0].type.val.base == 'str'

def test_parse_expr(parser):
    ast = parser.parse("~y = 1 + 2 * 3;")
    # RPN check: approx [1, 2, 3, *, +]
    assert len(ast.nodes[0].expr) == 5  # Stub assertion

def test_parse_pattern_tuple(parser):
    ast = parser.parse("let (a,b) = c;")
    pat = ast.nodes[0]
    assert pat.kind == 'tuple'
    assert len(pat.parts) == 2
    assert pat.parts[0].kind == 'var'

def test_parse_pattern_list(parser):
    ast = parser.parse("let [a,b] = c;")
    pat = ast.nodes[0]
    assert pat.kind == 'list'
    assert len(pat.parts) == 2

def test_parse_pattern_dict(parser):
    ast = parser.parse("let {k: v} = d;")
    pat = ast.nodes[0]
    assert pat.kind == 'dict'
    assert len(pat.parts) == 1

def test_parse_if(parser):
    ast = parser.parse("?x>0 { ~y=1; };")
    assert isinstance(ast.nodes[0], IfNode)
    assert len(ast.nodes[0].body) == 1

def test_parse_loop(parser):
    ast = parser.parse("*i=0..10 { ~y=i; };")
    assert isinstance(ast.nodes[0], LoopNode)
    assert ast.nodes[0].var == 'i'

def test_parse_macro(parser):
    ast = parser.parse("!macro inc { x + 1 };")
    assert isinstance(ast.nodes[0], MacroNode)
    assert ast.nodes[0].name == 'inc'
