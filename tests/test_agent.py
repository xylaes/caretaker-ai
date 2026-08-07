from caretaker_ai.agent import read_source_file, apply_patch, run_test_command


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


def test_apply_patch_plain(tmp_path):
    file_path = tmp_path / "test_file.py"
    content = "print('hello')"
    res = apply_patch(str(file_path), content)
    assert f"Successfully updated '{file_path}' with the new content." in res
    assert file_path.read_text(encoding="utf-8") == content


def test_apply_patch_markdown(tmp_path):
    file_path = tmp_path / "test_file_md.py"
    content = (
        "Some text before\n```python\nprint('hello markdown')\n```\nSome text after"
    )
    res = apply_patch(str(file_path), content)
    assert f"Successfully updated '{file_path}' with the new content." in res
    assert file_path.read_text(encoding="utf-8") == "print('hello markdown')"


def test_run_test_command_success():
    res = run_test_command("python -c \"print('success')\"")
    assert "Status: PASSED" in res
    assert "Exit Code: 0" in res
    assert "success" in res


def test_run_test_command_failure():
    res = run_test_command(
        "python -c \"import sys; sys.stderr.write('failed_err'); sys.exit(10)\""
    )
    assert "Status: FAILED" in res
    assert "Exit Code: 10" in res
    assert "failed_err" in res
