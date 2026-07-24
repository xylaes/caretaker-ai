from unittest.mock import MagicMock, patch
import pytest
from caretaker_ai.engine import GeminiHealer

def test_gemini_healer_init():
    # Test initialization with custom arguments
    healer = GeminiHealer(project_id="test-proj", location="europe-west1", model_name="gemini-test-model")
    assert healer.project_id == "test-proj"
    assert healer.location == "europe-west1"
    assert healer.model_name == "gemini-test-model"
    assert healer._client is None

def test_gemini_healer_client_property_caching():
    healer = GeminiHealer(project_id="test-proj", location="europe-west1")

    # Mock genai.Client
    with patch("caretaker_ai.engine.genai.Client") as mock_client_cls:
        mock_client_instance = MagicMock()
        mock_client_cls.return_value = mock_client_instance

        # Access client first time
        client1 = healer.client
        mock_client_cls.assert_called_once_with(
            vertexai=True,
            project="test-proj",
            location="europe-west1"
        )
        assert client1 == mock_client_instance

        # Access client second time (should be cached)
        client2 = healer.client
        mock_client_cls.assert_called_once() # Should not be called again
        assert client2 == mock_client_instance

def test_gemini_healer_generate_fix():
    healer = GeminiHealer(project_id="test-proj")

    # Mock genai.Client and the models.generate_content call
    with patch("caretaker_ai.engine.genai.Client") as mock_client_cls:
        mock_client_instance = MagicMock()
        mock_client_cls.return_value = mock_client_instance

        # Mock the chain: client.models.generate_content(...)
        mock_response = MagicMock()
        mock_response.text = "```python\ndef fixed_func():\n    return True\n```"
        mock_client_instance.models.generate_content.return_value = mock_response

        fixed_code = healer.generate_fix(
            file_path="app.py",
            file_content="def fixed_func():\n    return False",
            error_logs="AssertionError: assert False is True"
        )

        # Verify the mock call
        mock_client_instance.models.generate_content.assert_called_once()
        call_kwargs = mock_client_instance.models.generate_content.call_args[1]

        assert call_kwargs["model"] == "gemini-2.5-flash"
        assert "app.py" in call_kwargs["contents"]
        assert "AssertionError: assert False is True" in call_kwargs["contents"]
        assert ("def fixed_func():\n    return False" in call_kwargs["contents"] or
                "def fixed_func():\\n    return False" in call_kwargs["contents"])
        assert fixed_code == "```python\ndef fixed_func():\n    return True\n```"
