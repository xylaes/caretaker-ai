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
