import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from google.genai import types

from caretaker_ai.cli import main


def test_cli_target_file_not_exists(tmp_path):
    # Test that when the target file does not exist, it prints an error and exits with 1.
    non_existent_file = str(tmp_path / "non_existent.py")
    test_args = [
        "caretaker",
        "--test-command",
        "pytest",
        "--target-file",
        non_existent_file,
    ]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


def test_cli_success(tmp_path, capsys):
    # Setup target file
    target_file = tmp_path / "target.py"
    target_file.write_text("print('hello')", encoding="utf-8")

    test_args = [
        "caretaker",
        "--test-command",
        "pytest",
        "--target-file",
        str(target_file),
        "--project-id",
        "test-project",
        "--location",
        "test-location",
        "--model",
        "test-model",
        "--max-retries",
        "5",
    ]

    # Mock Runner run to yield custom events
    mock_event1 = MagicMock()
    mock_event1.content = types.Content(
        role="model", parts=[types.Part.from_text(text="Fixing the bug...")]
    )
    mock_event1.output = None

    mock_event2 = MagicMock()
    mock_event2.content = None
    mock_event2.output = "Running tests..."

    events = [mock_event1, mock_event2]

    mock_runner_instance = MagicMock()
    mock_runner_instance.run.return_value = events

    # Patch Runner init to return our mock runner instance
    with (
        patch(
            "caretaker_ai.cli.Runner", return_value=mock_runner_instance
        ) as mock_runner_class,
        patch.object(sys, "argv", test_args),
        patch.dict(os.environ, {}, clear=False),
    ):
        main()

        # Verify environment variables were set
        assert os.environ.get("GOOGLE_CLOUD_PROJECT") == "test-project"
        assert os.environ.get("GOOGLE_CLOUD_LOCATION") == "test-location"
        assert os.environ.get("GOOGLE_GENAI_MODEL") == "test-model"

        # Verify Runner was initialized with correct arguments
        mock_runner_class.assert_called_once()
        _, kwargs = mock_runner_class.call_args
        assert kwargs["app_name"] == "caretaker-ai"

        # Verify runner.run was called
        mock_runner_instance.run.assert_called_once()
        _, run_kwargs = mock_runner_instance.run.call_args
        assert "new_message" in run_kwargs
        assert "session_id" in run_kwargs

        query_msg = run_kwargs["new_message"]
        assert f"Repair the file '{str(target_file)}'" in query_msg.parts[0].text
        assert "using test command 'pytest'" in query_msg.parts[0].text
        assert "with max retries 5" in query_msg.parts[0].text

        # Verify standard output
        captured = capsys.readouterr()
        assert "Fixing the bug..." in captured.out
        assert "[Event] Running tests..." in captured.out
        assert "=== Caretaker AI self-healing loop finished ===" in captured.out
