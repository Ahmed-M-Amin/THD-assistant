import json
import uuid
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages chat sessions using JSON file storage."""

    def __init__(self, base_dir: str = "data/sessions"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self) -> Dict:
        """Create a new empty session."""
        session_id = str(uuid.uuid4())
        session = {
            "id": session_id,
            "title": "New Chat",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": [],
        }
        self.save_session(session)
        return session

    def save_session(self, session: Dict):
        """Save a session to disk."""
        try:
            session["updated_at"] = datetime.now().isoformat()

            # Auto-title logic: Use first user message if title is still "New Chat"
            if session["title"] == "New Chat" and len(session["messages"]) > 0:
                for msg in session["messages"]:
                    if msg["role"] == "user":
                        # Truncate to 30 chars
                        title = (
                            msg["content"][:30] + "..."
                            if len(msg["content"]) > 30
                            else msg["content"]
                        )
                        session["title"] = title
                        break

            file_path = self.base_dir / f"{session['id']}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(session, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save session {session.get('id')}: {e}")

    def load_session(self, session_id: str) -> Optional[Dict]:
        """Load a session by ID."""
        file_path = self.base_dir / f"{session_id}.json"
        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None

    def list_sessions(self) -> List[Dict]:
        """List all sessions sorted by updated_at desc."""
        sessions = []
        for file_path in self.base_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    sessions.append(
                        {
                            "id": data["id"],
                            "title": data.get("title", "Untitled"),
                            "updated_at": data.get("updated_at", ""),
                        }
                    )
            except Exception:
                continue

        # Sort by updated_at descending (newest first)
        sessions.sort(key=lambda x: x["updated_at"], reverse=True)
        return sessions

    def delete_session(self, session_id: str):
        """Delete a session file."""
        file_path = self.base_dir / f"{session_id}.json"
        if file_path.exists():
            file_path.unlink()
