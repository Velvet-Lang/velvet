import pytest
from velvet_ir_gen import VelvetIRGen
from velvet_parser import VelvetParser

@pytest.fixture
def ir_gen():
    parser = VelvetParser()
    code = "~x: int = 5;"
    ast = parser.parse(code)
    return VelvetIRGen(ast)

def test_type_map(ir_gen):
    ir = ir_gen.generate()
    assert ir['nodes'][0]['typ']['rust'] == 'i32'
    assert ir['nodes'][0]['typ']['java'] == 'int'

def test_async_func(ir_gen):
    code = "async !f(){ ^1 };"
    ast = VelvetParser().parse(code)
    ir = VelvetIRGen(ast).generate()
    assert ir['nodes'][0]['async'] == True

def test_match(ir_gen):
    code = "match x { 1 => y, _ => z };"
    ast = VelvetParser().parse(code)
    ir = VelvetIRGen(ast).generate()
    assert ir['nodes'][0]['type'] == 'match'
    assert len(ir['nodes'][0]['cases']) == 2

# Add tests for macro expansion, inline embed, etc.
