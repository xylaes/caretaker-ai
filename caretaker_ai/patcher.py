import difflib

class Patcher:
    @staticmethod
    def extract_code(response_text: str) -> str:
        """Extracts code from a markdown code block, handling fallbacks."""
        lines = response_text.splitlines()
        code_lines = []
        in_block = False
        for line in lines:
            if line.strip().startswith("```"):
                if not in_block:
                    in_block = True
                    continue
                else:
                    in_block = False
                    break
            elif in_block:
                code_lines.append(line)
        
        if not code_lines:
            # Fallback if no block found
            return response_text.strip()
        return "\n".join(code_lines)

    @staticmethod
    def generate_diff(original: str, corrected: str, filename: str) -> str:
        """Generates a unified diff string."""
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            corrected.splitlines(keepends=True),
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}"
        )
        return "".join(diff)

    @staticmethod
    def apply_patch(filepath: str, content: str):
        """Overwrites file content on disk."""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
