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

def test_apply_patch(tmp_path):
    # 1. Test writing new content to a non-existent file
    file_path = tmp_path / "new_file.py"
    content = "def hello():\n    print('Hello World')\n"

    Patcher.apply_patch(str(file_path), content)

    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == content

    # 2. Test overwriting existing content in a file
    new_content = "def hello():\n    print('Hello back!')\n"
    Patcher.apply_patch(str(file_path), new_content)

    assert file_path.read_text(encoding="utf-8") == new_content

    # 3. Test writing non-ASCII (UTF-8) characters to verify encoding
    unicode_content = "# coding: utf-8\n# 🌟 Testing unicode 🌟\n"
    Patcher.apply_patch(str(file_path), unicode_content)

    assert file_path.read_text(encoding="utf-8") == unicode_content
