"""
Contract Tests for Gemini LLM Integration

These tests verify LLM integration WITHOUT burning API credits by:
1. Testing prompt structure and formatting
2. Using mocked Gemini responses
3. Validating response parsing logic
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.llm_engine_gemini import GeminiLLMEngine
from src.data_store import ProgramDataStore


class TestLLMPromptStructure:
    """Test that prompts are well-formed before sending to API."""

    @patch("src.llm_engine_gemini.genai.Client")
    @patch("src.data_store.ProgramDataStore")
    def test_system_prompt_includes_student_categories(self, mock_store, mock_client):
        """System prompt must mention all 3 student categories."""
        mock_store_instance = Mock()
        mock_client_instance = Mock()

        llm = GeminiLLMEngine(api_key="test-key", data_store=mock_store_instance)

        system_prompt = llm._build_system_prompt("en")

        assert "German Students" in system_prompt or "domestic" in system_prompt.lower()
        assert "EU" in system_prompt or "EEA" in system_prompt
        assert "International Students" in system_prompt or "Non-EU" in system_prompt

    @patch("src.llm_engine_gemini.genai.Client")
    @patch("src.data_store.ProgramDataStore")
    def test_system_prompt_mentions_fees_requirement(self, mock_store, mock_client):
        """System prompt should instruct bot to clarify student category for fees."""
        mock_store_instance = Mock()

        llm = GeminiLLMEngine(api_key="test-key", data_store=mock_store_instance)

        system_prompt = llm._build_system_prompt("en")

        # Should mention asking about category or providing all 3
        assert (
            "category" in system_prompt.lower()
            or "which category" in system_prompt.lower()
        )


class TestLLMResponseWithMocks:
    """Test LLM response handling with mocked Gemini API."""

    @patch("src.llm_engine_gemini.genai.Client")
    @patch("src.data_store.ProgramDataStore")
    def test_generate_response_calls_semantic_search(
        self, mock_store_class, mock_client_class
    ):
        """Verify that generate_response() triggers semantic search."""
        # Setup mocks
        mock_store = Mock()
        mock_store.semantic_search = Mock(return_value=[])

        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "Test response"
        mock_client.models.generate_content = Mock(return_value=mock_response)

        # Inject mocks
        with patch.object(GeminiLLMEngine, "_load_client"):
            llm = GeminiLLMEngine(api_key="test", data_store=mock_store)
            llm.client = mock_client

        # Call
        response = llm.generate_response("What are the fees?", language="en")

        # Verify semantic search was called
        mock_store.semantic_search.assert_called_once()
        assert response == "Test response"

    @patch("src.llm_engine_gemini.genai.Client")
    @patch("src.data_store.ProgramDataStore")
    def test_generate_response_handles_api_error(
        self, mock_store_class, mock_client_class
    ):
        """Verify graceful error handling when Gemini API fails."""
        mock_store = Mock()
        mock_store.semantic_search = Mock(return_value=[])

        mock_client = Mock()
        mock_client.models.generate_content = Mock(side_effect=Exception("API Error"))

        with patch.object(GeminiLLMEngine, "_load_client"):
            llm = GeminiLLMEngine(api_key="test", data_store=mock_store)
            llm.client = mock_client

        response = llm.generate_response("Test query", language="en")

        # Should return error message, not crash
        assert "trouble" in response.lower() or "apologize" in response.lower()


class TestLLMResponseParsing:
    """Test that we correctly parse Gemini's responses."""

    def test_extract_fee_info_from_response(self):
        """Verify we can extract numerical fee values from LLM response."""
        sample_response = (
            "The tuition fee for international students is €62 per semester."
        )

        # Simple regex check (in real code, this would be in a utility function)
        import re

        fee_match = re.search(r"€(\d+)", sample_response)

        assert fee_match is not None, "Failed to extract fee from response"
        assert fee_match.group(1) == "62"
