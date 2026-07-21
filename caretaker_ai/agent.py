import os
import subprocess
import google.auth
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

# Initialize credentials
try:
    _, project_id = google.auth.default()
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
except Exception:
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "[placeholder]")

os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

def run_test_command(command: str) -> str:
    """Runs the specified test or build command on the application.

    Args:
        command: The exact command line string to execute.

    Returns:
        The stderr or stdout log output of the command.
    """
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    output = result.stderr if result.stderr.strip() else result.stdout
    success = "PASSED" if result.returncode == 0 else "FAILED"
    return f"Status: {success}\nExit Code: {result.returncode}\nOutput:\n{output}"

def read_source_file(file_path: str) -> str:
    """Reads the contents of the target source file to repair.

    Args:
        file_path: Path to the target source file.

    Returns:
        The content of the file.
    """
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' does not exist."
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def apply_patch(file_path: str, content: str) -> str:
    """Overwrites the target source file with new, corrected content.

    Args:
        file_path: Path to the target source file.
        content: The complete new content to write to the file.

    Returns:
        A success message indicating the file was updated.
    """
    # Simple extraction block in case LLM wraps it in markdown blocks
    if "```" in content:
        lines = content.splitlines()
        code_lines = []
        in_block = False
        for line in lines:
            if "```" in line and line.lstrip().startswith("```"):
                if not in_block:
                    in_block = True
                    continue
                else:
                    break
            elif in_block:
                code_lines.append(line)
        if code_lines:
            content = "\n".join(code_lines)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Successfully updated '{file_path}' with the new content."

root_agent = Agent(
    name="caretaker_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are Caretaker AI, an autonomous self-healing agent for unmaintained legacy software pipelines.
Your goal is to repair a bug in a target source file so that its test suite passes.

You have access to tools:
- `read_source_file`: to read the content of the file to fix.
- `run_test_command`: to run the test suite and get logs.
- `apply_patch`: to apply corrected code to the file.

Follow this execution loop:
1. Read the target file content using `read_source_file`.
2. Run the test command using `run_test_command` to get the initial error output.
3. If the test command shows success (Status: PASSED), stop! Explain that the code is healthy.
4. If it fails, analyze the error output and the code, write the complete corrected file, and apply the patch using `apply_patch`.
5. Run the test command again to verify.
6. If it still fails, repeat the loop. You have a maximum of 3 attempts to repair the file.
7. Finally, report a summary of whether you successfully fixed the file and the diff of your changes.
""",
    tools=[run_test_command, read_source_file, apply_patch],
)

app = App(
    root_agent=root_agent,
    name="caretaker-ai"
)
