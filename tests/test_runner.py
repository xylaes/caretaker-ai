from caretaker_ai.runner import CommandRunner

def test_command_runner_success():
    # Run a simple successful python command
    runner = CommandRunner('python -c "print(\'success\')"')
    success, output, code = runner.run()
    assert success is True
    assert "success" in output.strip()
    assert code == 0

def test_command_runner_failure():
    # Run a command that exits with code 42 and writes to stderr
    runner = CommandRunner('python -c "import sys; sys.stderr.write(\'error_log\'); sys.exit(42)"')
    success, output, code = runner.run()
    assert success is False
    assert "error_log" in output.strip()
    assert code == 42

def test_command_runner_injection(tmp_path):
    # Attempt a command injection that would create a file if shell=True was used
    canary_file = tmp_path / "injected.txt"
    command = f"python -c \"print('hello')\" ; touch {canary_file}"
    runner = CommandRunner(command)
    success, output, code = runner.run()
    # If shell injection worked, canary_file would exist. It must NOT exist.
    assert not canary_file.exists()
