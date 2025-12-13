"""
Unit Tests for src/session_manager.py

Tests session CRUD operations with mocked file I/O.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import json
from src.session_manager import SessionManager


class TestSessionManager:
    """Test SessionManager CRUD operations."""

    @patch("src.session_manager.Path.exists")
    @patch("src.session_manager.Path.mkdir")
    def test_init_creates_directory(self, mock_mkdir, mock_exists):
        """Test that __init__ creates sessions directory if missing."""
        mock_exists.return_value = False
        manager = SessionManager()
        mock_mkdir.assert_called_once()

    @patch("src.session_manager.open", new_callable=mock_open)
    @patch("src.session_manager.Path.exists", return_value=True)
    def test_save_session(self, mock_exists, mock_file):
        """Test saving a session to JSON."""
        manager = SessionManager()

        session_data = {
            "id": "test-123",
            "title": "Test Chat",
            "created_at": "2025-01-01T00:00:00",
            "messages": [{"role": "user", "content": "Hello"}],
        }

        manager.save_session(session_data)

        # Verify file was opened for writing
        mock_file.assert_called()
        handle = mock_file()
        handle.write.assert_called()

    @patch("src.session_manager.Path.exists", return_value=True)
    @patch(
        "src.session_manager.open",
        new_callable=mock_open,
        read_data='{"id": "test-123", "title": "Test", "messages": []}',
    )
    def test_load_session(self, mock_file, mock_exists):
        """Test loading a session from JSON."""
        manager = SessionManager()

        session = manager.load_session("test-123")

        assert session is not None
        assert session["id"] == "test-123"

    @patch("src.session_manager.Path.unlink")
    @patch("src.session_manager.Path.exists", return_value=True)
    def test_delete_session(self, mock_exists, mock_unlink):
        """Test deleting a session file."""
        manager = SessionManager()

        manager.delete_session("test-123")

        mock_unlink.assert_called_once()
