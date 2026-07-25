# caretaker_ai/devops_agent.py
# Conceptual outline for continuous self-healing DevOps agent

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini

# Placeholder for GitHub API calls
def fetch_github_issues(repo_name: str) -> list[dict]:
    """Fetches open bug reports and feature requests from the specified GitHub repository.

    Args:
        repo_name: Full repository name, e.g. "xylaes/caretaker-ai"

    Returns:
        A list of dictionaries representing issues with 'id', 'title', and 'description'.
    """
    # Uses PyGithub or requests to fetch issues labeled 'bug'
    return [
        {
            "id": 101,
            "title": "Calculator divide raises NameError",
            "description": "Running calc.divide(5, 2) raises NameError: name 'b' is not defined."
        }
    ]

def write_reproduction_test(issue_description: str, test_file_path: str) -> str:
    """Writes a new pytest test case that reproduces the described bug.

    Args:
        issue_description: The description of the bug from the GitHub issue.
        test_file_path: Path where the test file should be saved.

    Returns:
        A confirmation message showing the path where the test was written.
    """
    test_code = f"""import pytest
from legacy_app.calculator import Calculator

def test_reproduce_issue():
    calc = Calculator()
    # reproduction test from issue description:
    # {issue_description}
    assert calc.divide(6, 3) == 2.0
"""
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(test_code)
    return f"Reproduction test written to '{test_file_path}'"

def deploy_code(repo_name: str, branch_name: str, files_changed: list[str]) -> str:
    """Commits corrected code, pushes to GitHub, and submits a Pull Request.

    Args:
        repo_name: The target repository name.
        branch_name: Target branch name.
        files_changed: List of files that were modified.

    Returns:
        A success message indicating the PR URL.
    """
    # Runs git commands to push changes and invokes GitHub API to create a PR
    return f"Successfully pushed branch '{branch_name}' and created Pull Request on '{repo_name}'"

devops_agent = Agent(
    name="devops_agent",
    model=Gemini(model="gemini-2.5-flash"),
    instruction="""You are an autonomous DevOps and Self-Healing Agent. 
Your goal is to monitor a repository, identify issues, write a reproduction test, heal the bug, verify the test passes, and deploy the fix.

Execution loop:
1. Poll for open bug reports using `fetch_github_issues`.
2. For each bug, write a reproduction test using `write_reproduction_test`.
3. Use the self-healing loop tools (read_source_file, run_test_command, apply_patch) to repair the target file until the reproduction test passes.
4. Once verified healthy, deploy the changes and merge the fix back to the repository using `deploy_code`.
""",
    tools=[fetch_github_issues, write_reproduction_test, deploy_code]
)

app = App(
    root_agent=devops_agent,
    name="caretaker-devops"
)
