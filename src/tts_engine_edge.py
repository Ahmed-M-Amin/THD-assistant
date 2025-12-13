"""TTS engine using Microsoft Edge TTS (edge-tts)."""

import logging
import asyncio
import edge_tts
import io
from pydub import AudioSegment

logger = logging.getLogger(__name__)


class EdgeTTSEngine:
    """Text-to-Speech engine using Microsoft Edge TTS (Neural Voices)."""

    def __init__(self, voice_preference: str = "female"):
        """
        Initialize the Edge TTS engine.

        Args:
            voice_preference: Voice preference ("female" or "male")
        """
        self.voice_preference = voice_preference

        # Configure natural-sounding neural voices
        self.voices = {
            "en": {
                "female": "en-US-AriaNeural",  # Natural, professional female voice
                "male": "en-US-GuyNeural",
            },
            "de": {
                "female": "de-DE-KatjaNeural",  # Natural German female voice
                "male": "de-DE-ConradNeural",
            },
        }

        logger.info(f"✓ Edge TTS engine initialized (preference: {voice_preference})")

    def _get_voice(self, language: str) -> str:
        """Get the appropriate voice for the language."""
        # Default to English, and handle non-string or None language inputs
        lang_code = "en"
        if isinstance(language, str) and language:
            lang_code = language.lower()[:2]

        logger.debug(f"Attempting to find voice for language code: '{lang_code}'")

        # Get the dictionary of voices for the language, falling back to English
        lang_voices = self.voices.get(lang_code, self.voices["en"])
        if lang_code not in self.voices:
            logger.warning(
                f"Language '{lang_code}' not found in voices, defaulting to 'en'."
            )

        # Get the specific voice based on preference, falling back to the language's female voice
        voice = lang_voices.get(self.voice_preference, lang_voices.get("female"))

        logger.info(
            f"Selected voice: '{voice}' for language '{lang_code}' with preference '{self.voice_preference}'"
        )
        return voice

    def synthesize(self, text: str, language: str = "en") -> bytes:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize
            language: Language code ("en" or "de")

        Returns:
            Audio data as bytes (WAV format, 24kHz, mono, int16)
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for synthesis")
            return b""

        try:
            # Get appropriate voice
            voice = self._get_voice(language)
            logger.debug(f"Using voice: {voice} for language: {language}")

            # Run async synthesis in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                audio_data = loop.run_until_complete(
                    self._synthesize_async(text, voice)
                )
            finally:
                loop.close()

            if audio_data:
                logger.info(f"✓ Synthesized {len(audio_data)} bytes of audio")
                return audio_data
            else:
                logger.error("Synthesis returned no audio data")
                return b""

        except Exception as e:
            logger.error(f"Edge TTS synthesis failed: {e}")
            return b""

    async def _synthesize_async(self, text: str, voice: str) -> bytes:
        """
        Async synthesis using edge-tts.

        Args:
            text: Text to synthesize
            voice: Voice name

        Returns:
            Audio data as bytes (WAV format)
        """
        try:
            # Create communicate object
            communicate = edge_tts.Communicate(text, voice)

            # Collect audio chunks
            audio_chunks = []
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_chunks.append(chunk["data"])

            if not audio_chunks:
                logger.error("No audio chunks received from edge-tts")
                return b""

            # Combine chunks
            mp3_data = b"".join(audio_chunks)

            # Convert MP3 to WAV (24kHz, mono, int16) for compatibility
            audio = AudioSegment.from_mp3(io.BytesIO(mp3_data))
            audio = audio.set_channels(1)  # Mono
            audio = audio.set_frame_rate(24000)  # 24kHz

            # Export as WAV bytes
            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format="wav")
            wav_data = wav_buffer.getvalue()

            return wav_data

        except Exception as e:
            logger.error(f"Async synthesis error: {e}")
            return b""

    def set_voice_preference(self, preference: str):
        """
        Change voice preference.

        Args:
            preference: "female" or "male"
        """
        if preference in ["female", "male"]:
            self.voice_preference = preference
            logger.info(f"Voice preference updated to: {preference}")
        else:
            logger.warning(f"Invalid voice preference: {preference}")
