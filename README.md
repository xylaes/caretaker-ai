# Caretaker AI

Autonomous self-healing CLI tool for unmaintained and legacy software pipelines.

## Overview

Caretaker AI acts as an autonomous caretaker for software that is no longer seeing active developer support. It integrates directly into test or build pipelines to catch failures, analyze the failure stack traces, query a Large Language Model (Gemini) to generate targeted fixes, apply those patches, and verify that the build is restored to a healthy state.

## Installation

Install in editable mode for development:

```bash
pip install -e .[dev]
```

## Usage

Run the self-healing caretaker loop:

```bash
caretaker --test-command "pytest" --target-file "legacy_app/calculator.py"
```

### Options

*   `--test-command`: (Required) The exact command line string to run tests or build (e.g. `"npm test"` or `"pytest"`).
*   `--target-file`: (Required) Path to the file containing the bug that needs to be repaired.
*   `--project-id`: Google Cloud project ID (Vertex AI).
*   `--location`: Google Cloud region for Vertex AI API (default: `us-central1`).
*   `--model`: Gemini model name to use (default: `gemini-2.5-flash`).
*   `--max-retries`: Maximum self-healing attempts to make before giving up (default: `3`).
