"""
Local Voice Handler - Uses SpeechRecognition's built-in microphone (Google Web Speech API)
Reverted from Whisper due to performance issues, but kept THD term corrections.
"""

import sounddevice as sd
import numpy as np
import speech_recognition as sr
import logging
import re
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class AudioDeviceError(Exception):
    pass


class LocalVoiceHandler:
    """Voice handler using SpeechRecognition's built-in microphone recording."""

    # Common misrecognitions for THD-related terms
    CORRECTIONS = {
        # Bachelor program terms
        r"\bbatchel\b": "bachelor",
        r"\bbachler\b": "bachelor",
        r"\bbachlor\b": "bachelor",
        # Fees terms
        r"\bfeast\b": "fees",
        r"\bfees\b": "fees",
        # Master terms
        r"\bmasters\b": "master",
        # THD terms
        r"\bthd\b": "THD",
        r"\bth d\b": "THD",
        r"\btech\s*deggendorf\b": "Technische Hochschule Deggendorf",
        # Program terms
        r"\bcomputer\s*sience\b": "computer science",
        r"\bcyber\s*secuirty\b": "cyber security",
        r"\bcyber\s*secutiry\b": "cyber security",
    }

    def __init__(self, device_index: int = None, sample_rate: int = 44100):
        self.device_index = device_index
        self.sample_rate = sample_rate
        self.recognizer = sr.Recognizer()

        # Settings for voice detection (tuned for patience)
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.pause_threshold = 2.0
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.3

        logger.info(
            f"LocalVoiceHandler initialized (Google Speech, sample_rate: {sample_rate})"
        )

    def _fix_thd_terms(self, text: str) -> str:
        """Fix common misrecognitions for THD-related terms."""
        for pattern, replacement in self.CORRECTIONS.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def listen_once(
        self, listen_timeout: float = 30.0, language: str = "en"
    ) -> Tuple[Optional[str], Optional[np.ndarray]]:
        """Listen for speech and transcribe using Google Speech."""
        language_map = {"en": "en-US", "de": "de-DE"}
        google_language = language_map.get(language, "en-US")

        try:
            # Use default microphone (device_index=None)
            with sr.Microphone(sample_rate=self.sample_rate) as source:
                logger.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)

                logger.info(f"🎤 Listening... (language: {google_language})")

                try:
                    audio = self.recognizer.listen(
                        source, timeout=listen_timeout, phrase_time_limit=60
                    )
                    logger.info("Speech detected, transcribing...")

                    text = self.recognizer.recognize_google(
                        audio, language=google_language
                    )

                    # Fix common misrecognitions
                    text = self._fix_thd_terms(text)

                    logger.info(f"✓ Transcribed: {text}")

                    # Convert audio to numpy for playback/storage
                    audio_data = (
                        np.frombuffer(audio.get_raw_data(), dtype=np.int16).astype(
                            np.float32
                        )
                        / 32768.0
                    )
                    return text, audio_data

                except sr.WaitTimeoutError:
                    logger.info("No speech detected (timeout)")
                    return None, None
                except sr.UnknownValueError:
                    logger.warning(
                        "Google Speech Recognition could not understand audio"
                    )
                    return "", None
                except sr.RequestError as e:
                    logger.error(f"Google Speech Recognition request failed: {e}")
                    return None, None

        except Exception as e:
            logger.error(f"Microphone error: {e}")
            raise AudioDeviceError(str(e))

    def play_audio(self, audio_bytes):
        """Play audio through speakers."""
        try:
            import io
            import soundfile as sf

            audio_data, sr_rate = sf.read(io.BytesIO(audio_bytes))
            audio_data = audio_data * 1.5
            audio_data = np.clip(audio_data, -1.0, 1.0)

            sd.play(audio_data, sr_rate)
            sd.wait()

        except Exception as e:
            logger.error(f"Play audio error: {e}")
