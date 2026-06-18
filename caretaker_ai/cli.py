import argparse
import sys
import os
from caretaker_ai.runner import CommandRunner
from caretaker_ai.engine import GeminiHealer
from caretaker_ai.patcher import Patcher

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

    print("=== Caretaker AI Self-Healing Loop ===")
    runner = CommandRunner(args.test_command)
    
    # 1. Run initial tests
    success, output, code = runner.run()
    if success:
        print("[OK] All tests passed! Code is healthy. No healing needed.")
        sys.exit(0)
        
    print(f"\n[!] Test/Build command failed (exit code: {code})")
    print(f"Error logs:\n{output}\n")
    
    # Check if target file exists
    if not os.path.exists(args.target_file):
        print(f"Error: Target file '{args.target_file}' does not exist.", file=sys.stderr)
        sys.exit(1)
        
    healer = GeminiHealer(
        project_id=args.project_id,
        location=args.location,
        model_name=args.model
    )
    
    retries = 0
    while not success and retries < args.max_retries:
        retries += 1
        print(f"\n--- Healing Attempt {retries}/{args.max_retries} ---")
        
        # Read file
        with open(args.target_file, "r", encoding="utf-8") as f:
            original_code = f.read()
            
        # Call Gemini
        raw_response = healer.generate_fix(args.target_file, original_code, output)
        corrected_code = Patcher.extract_code(raw_response)
        
        # Calculate proposed diff
        diff = Patcher.generate_diff(original_code, corrected_code, args.target_file)
        if not diff.strip():
            print("Gemini proposed no changes. Exiting.")
            sys.exit(1)
            
        print("\nProposed patch:")
        print(diff)
        
        # Apply patch
        print(f"Applying patch to '{args.target_file}'...")
        Patcher.apply_patch(args.target_file, corrected_code)
        
        # Re-verify
        success, output, code = runner.run()
        if success:
            print(f"\n[OK] SUCCESS: Self-healing succeeded on attempt {retries}! All tests pass.")
            sys.exit(0)
        else:
            print(f"\n[!] Patch failed. Error logs:\n{output}\n")
            
    print("\n[FAIL] Caretaker failed to heal the application within the retry limit.")
    sys.exit(1)

if __name__ == "__main__":
    main()
