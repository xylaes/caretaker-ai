import argparse
import sys
import os
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types

from caretaker_ai.agent import root_agent

def main():
    parser = argparse.ArgumentParser(
        description="Caretaker AI: Autonomous self-healing CLI for unmaintained software pipelines."
    )
    parser.add_argument(
        "--test-command",
        required=True,
        help="Command to run tests or build (e.g., 'pytest' or 'npm test')"
    )
    parser.add_argument(
        "--target-file",
        required=True,
        help="Path to the source file to repair (e.g., 'legacy_app/calculator.py')"
    )
    parser.add_argument(
        "--project-id",
        default="gen-lang-client-0720914706",
        help="Google Cloud project ID (Vertex AI)"
    )
    parser.add_argument(
        "--location",
        default="us-central1",
        help="Google Cloud location for Vertex AI API"
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        help="Gemini model name to use"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum self-healing loop retries"
    )

    args = parser.parse_args()

    # Configure Google Cloud environment if parameters provided
    if args.project_id:
        os.environ["GOOGLE_CLOUD_PROJECT"] = args.project_id
    if args.location:
        os.environ["GOOGLE_CLOUD_LOCATION"] = args.location
    if args.model:
        os.environ["GOOGLE_GENAI_MODEL"] = args.model

    print("=== Caretaker AI Self-Healing Loop ===")
    print(f"Target File: {args.target_file}")
    print(f"Test Command: {args.test_command}")
    print(f"Max Retries: {args.max_retries}")
    print("--------------------------------------")

    # Check if target file exists
    if not os.path.exists(args.target_file):
        print(f"Error: Target file '{args.target_file}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Initialize the ADK Session and Runner
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(user_id="cli_user", app_name="caretaker-ai")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="caretaker-ai")

    query = f"Repair the file '{args.target_file}' using test command '{args.test_command}' with max retries {args.max_retries}"
    message = types.Content(
        role="user", parts=[types.Part.from_text(text=query)]
    )

    # Execute the self-healing loop
    events = runner.run(
        new_message=message,
        user_id="cli_user",
        session_id=session.id,
        run_config=RunConfig(streaming_mode=StreamingMode.SSE),
    )

    for event in events:
        if event.content and event.content.parts:
            text = "".join(part.text for part in event.content.parts if part.text)
            if text:
                print(text, end="", flush=True)
        elif event.output:
            # Handle status outputs or tool executions
            print(f"\n[Event] {event.output}")

    print("\n--------------------------------------")
    print("=== Caretaker AI self-healing loop finished ===")

if __name__ == "__main__":
    main()
