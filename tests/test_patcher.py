from caretaker_ai.patcher import Patcher

def test_extract_code_with_markdown():
    response = """Here is the corrected code:
```python
def multiply(a, b):
    return a * b
```
Let me know if this works!"""
    extracted = Patcher.extract_code(response)
    expected = "def multiply(a, b):\n    return a * b"
    assert extracted.strip() == expected.strip()

def test_extract_code_fallback():
    response = "def add(a, b):\n    return a + b"
    extracted = Patcher.extract_code(response)
    assert extracted == response

def test_generate_diff():
    original = "def foo():\n    return 1"
    corrected = "def foo():\n    return 2"
    diff = Patcher.generate_diff(original, corrected, "foo.py")
    assert "-    return 1" in diff
    assert "+    return 2" in diff
