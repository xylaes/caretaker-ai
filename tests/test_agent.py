from caretaker_ai.agent import read_source_file


def test_read_source_file_success(tmp_path):
    # Setup test file with valid content, including unicode characters
    file_path = tmp_path / "valid_file.txt"
    content = "Hello, world! 🌟 This is a test file."
    file_path.write_text(content, encoding="utf-8")

    # Read the file and assert content match
    result = read_source_file(str(file_path))
    assert result == content


def test_read_source_file_not_found(tmp_path):
    # Setup a non-existent file path
    non_existent_path = tmp_path / "non_existent_file.txt"

    # Verify we get the expected error message (matching the '!' ending in agent.py)
    result = read_source_file(str(non_existent_path))
    assert result == f"Error: File '{non_existent_path}' does not exist!"


def test_apply_patch_no_markdown(tmp_path):
    from caretaker_ai.agent import apply_patch

    file_path = tmp_path / "test.py"
    content = "def hello():\n    print('world')"
    res = apply_patch(str(file_path), content)
    assert file_path.read_text(encoding="utf-8") == content
    assert "Successfully updated" in res


def test_apply_patch_standard_markdown(tmp_path):
    from caretaker_ai.agent import apply_patch

    file_path = tmp_path / "test.py"
    content = "Some explanation before.\n```python\ndef hello():\n    print('world')\n```\nSome explanation after."
    apply_patch(str(file_path), content)
    assert file_path.read_text(encoding="utf-8") == "def hello():\n    print('world')"


def test_apply_patch_indented_markdown_marker(tmp_path):
    from caretaker_ai.agent import apply_patch

    file_path = tmp_path / "test.py"
    content = "   ```python\ndef hello():\n    print('world')\n   ```"
    apply_patch(str(file_path), content)
    assert file_path.read_text(encoding="utf-8") == "def hello():\n    print('world')"


def test_apply_patch_multiple_markdown_blocks(tmp_path):
    from caretaker_ai.agent import apply_patch

    file_path = tmp_path / "test.py"
    content = "```python\nblock1\n```\n```python\nblock2\n```"
    apply_patch(str(file_path), content)
    assert file_path.read_text(encoding="utf-8") == "block1"


def test_apply_patch_unclosed_markdown_block(tmp_path):
    from caretaker_ai.agent import apply_patch

    file_path = tmp_path / "test.py"
    content = "```python\ndef hello():\n    print('world')"
    apply_patch(str(file_path), content)
    assert file_path.read_text(encoding="utf-8") == "def hello():\n    print('world')"


def test_apply_patch_empty_markdown_block(tmp_path):
    from caretaker_ai.agent import apply_patch

    file_path = tmp_path / "test.py"
    content = "```python\n```"
    apply_patch(str(file_path), content)
    # Since block is empty, code_lines is empty, so content remains unchanged.
    assert file_path.read_text(encoding="utf-8") == "```python\n```"
