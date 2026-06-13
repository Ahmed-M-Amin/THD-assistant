"""Background worker for live voice chat (smooth playback + instant stop)."""

import logging
import threading
import time
from typing import Callable, Dict, Optional

from src.local_voice_handler import AudioDeviceError, LocalVoiceHandler

logger = logging.getLogger(__name__)


class LiveChatWorker:
    """Runs the listen → think → speak loop off the Streamlit main thread."""

    def __init__(
        self,
        voice_handler: LocalVoiceHandler,
        manager,
        language: str,
        session: Dict,
        save_session: Callable[[], None],
    ):
        self.voice_handler = voice_handler
        self.manager = manager
        self.language = language
        self.session = session
        self.save_session = save_session

        self.stop_event = threading.Event()
        self.status = "starting"
        self.error: Optional[str] = None
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self):
        if self.is_running:
            return
        self.stop_event.clear()
        self.error = None
        self.status = "starting"
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.stop_event.set()
        self.voice_handler.stop_playback()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def _append_message(self, role: str, content: str):
        with self._lock:
            self.session["messages"].append({"role": role, "content": content})
        self.save_session()

    def _run_loop(self):
        goodbye_phrases = [
            "goodbye",
            "bye",
            "exit",
            "quit",
            "stop",
            "tschüss",
            "auf wiedersehen",
        ]

        try:
            while not self.stop_event.is_set():
                self.status = "listening"
                self.voice_handler.stop_playback()
                time.sleep(0.25)
                try:
                    text, audio_data = self.voice_handler.listen_once(
                        listen_timeout=30.0, language=self.language
                    )
                except AudioDeviceError as e:
                    self.error = str(e)
                    self.status = "error"
                    return

                if self.stop_event.is_set():
                    break

                if text is None and audio_data is None:
                    self.status = "no_voice"
                    time.sleep(2)
                    continue

                if audio_data is None:
                    self.status = "unclear"
                    time.sleep(2)
                    continue

                self.status = "thinking"
                if self.stop_event.is_set():
                    break

                text, response, audio_response = self.manager.process_voice_query(
                    audio_data,
                    preferred_language=self.language,
                    sample_rate=self.voice_handler.sample_rate,
                )

                if not text:
                    self.status = "unclear"
                    time.sleep(2)
                    continue

                if any(p in text.lower() for p in goodbye_phrases):
                    self._append_message("user", text)
                    self._append_message("assistant", "Goodbye!")
                    self.status = "stopped"
                    break

                self._append_message("user", text)
                self._append_message("assistant", response)

                if self.stop_event.is_set():
                    break

                if audio_response:
                    self.status = "speaking"
                    self.voice_handler.play_audio_interruptible(
                        audio_response, self.stop_event
                    )
                    time.sleep(0.4)

                if self.stop_event.is_set():
                    break

        except Exception as e:
            logger.error(f"Live chat worker error: {e}", exc_info=True)
            self.error = str(e)
            self.status = "error"
