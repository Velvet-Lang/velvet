import pytest
from utils.inline_exec import InlineExecutor

@pytest.fixture
def executor():
    exec = InlineExecutor()
    exec.allow_langs = set(exec.supported_langs)  # Allow all for tests
    return exec

def test_exec_python(executor):
    results = executor.execute([("python", 'print("test")')], "test.vel")
    assert results[0]['stdout'] == "test"
    assert results[0]['code'] == 0

def test_exec_rust(executor):
    results = executor.execute([("rust", 'println!("Rust test");')], "test.vel")
    assert "Rust test" in results[0]['stdout']

def test_exec_java(executor):
    results = executor.execute([("java", 'System.out.println("Java test");')], "test.vel")
    assert "Java test" in results[0]['stdout']

def test_tmp_cleanup(executor):
    executor.execute([], "test.vel")
    assert not os.path.exists("tmp")  # No leftovers

def test_error_handling(executor):
    results = executor.execute([("python", 'raise ValueError("err")')], "test.vel")
    assert results[0]['code'] != 0
    assert "err" in results[0]['stderr']

# Add tests for all langs
