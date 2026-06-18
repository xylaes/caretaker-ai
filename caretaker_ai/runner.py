import os
import subprocess
import sys

class CommandRunner:
    def __init__(self, command: str, cwd: str = "."):
        self.command = command
        self.cwd = cwd

    def run(self):
        """Runs the test command and returns (success, output, returncode)."""
        result = subprocess.run(
            self.command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=self.cwd
        )
        success = (result.returncode == 0)
        # Combine stdout and stderr if both exist, prioritizing stderr if it contains traces
        output = result.stderr if result.stderr.strip() else result.stdout
        return success, output, result.returncode
