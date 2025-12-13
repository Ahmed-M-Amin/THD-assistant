"""
Unit Tests for src/models.py

Tests Pydantic model validation edge cases and data transformations.
"""

import pytest
from pydantic import ValidationError
from src.models import Program, Fees, FeeCategory


class TestProgramModel:
    """Test Program model validation."""

    def test_minimal_valid_program(self):
        """Test creating a program with only required fields."""
        program = Program(
            code="TEST001",
            title="Test Program",
            degree_level="bachelor",
            faculty="Test Faculty",
            language_of_instruction="English",
            duration_semesters=6,
            ects_total=180,
            intakes=[],  # Required field
        )
        assert program.code == "TEST001"
        assert program.degree_level == "bachelor"

    def test_to_context_string_includes_fees(self):
        """Test that to_context_string() includes fee information."""
        program = Program(
            code="TEST001",
            title="Test",
            degree_level="bachelor",
            faculty="Test",
            language_of_instruction="English",
            duration_semesters=6,
            ects_total=180,
            intakes=[],
            fees=Fees(
                domestic_german=FeeCategory(
                    tuition_per_semester="0", service_fee_per_semester="62"
                ),
                eu_eea=FeeCategory(
                    tuition_per_semester="0", service_fee_per_semester="62"
                ),
                international_non_eu=FeeCategory(
                    tuition_per_semester="0", service_fee_per_semester="62"
                ),
            ),
        )

        context = program.to_context_string()
        assert "fees" in context.lower()
        assert "62" in context  # Service fee amount


class TestFeeCategory:
    """Test fee structure validation."""

    def test_zero_fees_valid(self):
        """Test that zero fees (free tuition) is valid."""
        fee = FeeCategory(tuition_per_semester="0", service_fee_per_semester="62")
        assert fee.tuition_per_semester == "0"
