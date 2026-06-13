"""
Local Voice Handler - microphone capture and speaker playback for live chat.
"""

import logging
import re
from typing import Optional, Tuple

import numpy as np
import sounddevice as sd
import speech_recognition as sr

logger = logging.getLogger(__name__)


class AudioDeviceError(Exception):
    pass


class LocalVoiceHandler:
    """Voice handler using SpeechRecognition's built-in microphone recording."""

    CORRECTIONS = {
        r"\bbatchel\b": "bachelor",
        r"\bbachler\b": "bachelor",
        r"\bbachlor\b": "bachelor",
        r"\bfeast\b": "fees",
        r"\bfees\b": "fees",
        r"\bmasters\b": "master",
        r"\bthd\b": "THD",
        r"\bth d\b": "THD",
        r"\btech\s*deggendorf\b": "Technische Hochschule Deggendorf",
        r"\bcomputer\s*sience\b": "computer science",
        r"\bcyber\s*secuirty\b": "cyber security",
        r"\bcyber\s*secutiry\b": "cyber security",
    }

    def __init__(self, device_index: int = None, sample_rate: int = 16000):
        self.device_index = device_index
        self.sample_rate = sample_rate
        self.recognizer = sr.Recognizer()

        # Tune for shorter, cleaner conversational turns.
        self.recognizer.energy_threshold = 150
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.2
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5

        logger.info(
            f"LocalVoiceHandler initialized (sample_rate: {sample_rate}, device_index: {device_index})"
        )

    def fix_thd_terms(self, text: str) -> str:
        """Fix common misrecognitions for THD-related terms."""
        for pattern, replacement in self.CORRECTIONS.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def listen_once(
        self, listen_timeout: float = 30.0, language: str = "en"
    ) -> Tuple[Optional[str], Optional[np.ndarray]]:
        """Listen once and return captured audio for the shared STT pipeline."""
        _ = language

        try:
            with sr.Microphone(
                device_index=self.device_index, sample_rate=self.sample_rate
            ) as source:
                logger.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                logger.info("Listening for speech...")

                try:
                    audio = self.recognizer.listen(
                        source, timeout=listen_timeout, phrase_time_limit=15
                    )
                    logger.info("Speech detected, preparing audio buffer...")

                    audio_data = (
                        np.frombuffer(audio.get_raw_data(), dtype=np.int16).astype(
                            np.float32
                        )
                        / 32768.0
                    )
                    return "", audio_data

                except sr.WaitTimeoutError:
                    logger.info("No speech detected (timeout)")
                    return None, None
                except sr.UnknownValueError:
                    logger.warning("Speech could not be understood during capture")
                    return "", None
                except sr.RequestError as e:
                    logger.error(f"Speech recognition request failed: {e}")
                    return None, None

        except Exception as e:
            logger.error(f"Microphone error: {e}")
            raise AudioDeviceError(str(e))

    def _decode_audio(self, audio_bytes):
        """Decode audio bytes to mono float32 suitable for playback."""
        import io

        import soundfile as sf

        audio_data, sr_rate = sf.read(io.BytesIO(audio_bytes), dtype="float32")
        if audio_data.ndim > 1:
            audio_data = audio_data.mean(axis=1)

        peak = float(np.max(np.abs(audio_data))) if audio_data.size else 0.0
        if peak > 1.0:
            audio_data = audio_data / peak * 0.95
        elif 0.0 < peak < 0.2:
            audio_data = audio_data / peak * 0.9

        return np.ascontiguousarray(audio_data, dtype=np.float32), int(sr_rate)

    def play_audio(self, audio_bytes):
        """Play audio through speakers (blocking until finished)."""
        self.play_audio_interruptible(audio_bytes)

    def play_audio_interruptible(self, audio_bytes, stop_event=None) -> bool:
        """
        Play audio and optionally stop when stop_event is set.
        Returns True if playback finished, False if interrupted.
        """
        try:
            audio_data, sr_rate = self._decode_audio(audio_bytes)
            if audio_data.size == 0:
                logger.warning("No audio samples to play")
                return True

            duration = len(audio_data) / float(sr_rate)
            logger.info(f"Playing {duration:.1f}s of audio at {sr_rate} Hz")

            chunk_size = 4096
            with sd.OutputStream(
                samplerate=sr_rate,
                channels=1,
                dtype="float32",
                blocksize=chunk_size,
            ) as stream:
                for start in range(0, len(audio_data), chunk_size):
                    if stop_event is not None and stop_event.is_set():
                        break
                    stream.write(audio_data[start : start + chunk_size])

            if stop_event is not None and stop_event.is_set():
                return False
            return True
        except Exception as e:
            logger.error(f"Play audio error: {e}")
            return False

    def play_audio_nonblocking(self, audio_bytes):
        """Start audio playback without blocking."""
        try:
            audio_data, sr_rate = self._decode_audio(audio_bytes)
            sd.play(audio_data, sr_rate)
        except Exception as e:
            logger.error(f"Play audio error: {e}")

    def is_playing(self) -> bool:
        """Return True while speaker output is active."""
        try:
            stream = sd.get_stream()
            return stream is not None and stream.active
        except Exception:
            return False

    def stop_playback(self):
        """Stop any in-progress speaker output."""
        pass
