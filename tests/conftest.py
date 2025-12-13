"""Shared fixtures and configuration for all tests."""

import pytest
from pathlib import Path
import yaml
from src.models import ProgramMetadata


@pytest.fixture
def sample_program_yaml():
    """Minimal valid program YAML for testing."""
    return {
        "program": {
            "code": "test_prog_001",
            "title": "Test Program",
            "degree_level": "bachelor",
            "faculty": "Test Faculty",
            "language_of_instruction": "English",
            "duration_semesters": 6,
            "ects_total": 180,
        }
    }


@pytest.fixture
def data_dir():
    """Path to the actual data directory."""
    return Path("data/programs")


@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API response for LLM tests."""
    return "The tuition fee for international students is €62/semester."
