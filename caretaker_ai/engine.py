from google import genai

class GeminiHealer:
    def __init__(self, project_id: str, location: str = "us-central1", model_name: str = "gemini-2.5-flash"):
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        self._client = None

    @property
    def client(self):
        if self._client is None:
            # We use Vertex AI backend powered by Active gcloud credentials
            self._client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location
            )
        return self._client

    def generate_fix(self, file_path: str, file_content: str, error_logs: str) -> str:
        """Sends code and error logs to Gemini and returns the generated patch suggestions."""
        prompt = f"""You are an autonomous caretaker agent for legacy/EOL software.
The application's test suite or build command has failed. Your goal is to patch the code in `{file_path}` to fix the bug and make the tests pass.

Here is the error/test failure output:
```
{error_logs}
```

Here is the complete source code of the file `{file_path}`:
```python
{file_content}
```

Please analyze the failure, locate the bug, and write the corrected version of `{file_path}`.
Rules:
1. Return ONLY the complete corrected code.
2. Place the corrected code inside a ```python ... ``` code block (or matching language code block).
3. Do not include any explanations, introduction, markdown outside the code block, or other notes.
"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text
