from caretaker_ai.devops_agent import (
    fetch_github_issues,
    write_reproduction_test,
    deploy_code,
    devops_agent,
    app
)

def test_fetch_github_issues():
    # Call the fetch_github_issues function
    issues = fetch_github_issues("xylaes/caretaker-ai")

    # Assert that it returns a list with the expected keys
    assert isinstance(issues, list)
    assert len(issues) == 1
    issue = issues[0]
    assert issue["id"] == 101
    assert "Calculator divide" in issue["title"]
    assert "divide(5, 2)" in issue["description"]

def test_write_reproduction_test(tmp_path):
    # Setup test file path using tmp_path (which is clean and safe)
    test_file = tmp_path / "test_reproduce_bug.py"
    issue_desc = "Running calc.divide(5, 2) raises NameError: name 'b' is not defined."

    # Call write_reproduction_test
    result = write_reproduction_test(issue_desc, str(test_file))

    # Verify the return message
    assert f"Reproduction test written to '{test_file}'" in result

    # Verify the file was written and contains the expected code
    assert test_file.exists()
    content = test_file.read_text()
    assert "import pytest" in content
    assert "from legacy_app.calculator import Calculator" in content
    assert "test_reproduce_issue" in content
    assert "Running calc.divide(5, 2) raises NameError: name 'b' is not defined." in content
    assert "assert calc.divide(6, 3) == 2.0" in content

def test_deploy_code():
    repo = "xylaes/caretaker-ai"
    branch = "fix-calculator-divide"
    files = ["legacy_app/calculator.py"]

    # Call deploy_code
    result = deploy_code(repo, branch, files)

    # Verify the return message
    assert "Successfully pushed branch" in result
    assert branch in result
    assert repo in result

def test_devops_agent_config():
    # Verify devops_agent properties
    assert devops_agent.name == "devops_agent"
    assert "autonomous DevOps and Self-Healing Agent" in devops_agent.instruction

    # Verify that the expected tools are attached
    tools = devops_agent.tools
    tool_names = [t.__name__ for t in tools]
    assert "fetch_github_issues" in tool_names
    assert "write_reproduction_test" in tool_names
    assert "deploy_code" in tool_names

def test_app_config():
    # Verify app properties
    assert app.name == "caretaker-devops"
    assert app.root_agent == devops_agent
