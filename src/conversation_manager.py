"""Conversation manager to orchestrate STT, LLM, and TTS engines."""

import logging
import numpy as np
import re
from typing import Optional

from src.llm_engine_gemini import GeminiLLMEngine
from src.models import ConversationContext
from src.response_cache import ResponseCache

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manages the complete conversation flow."""

    def __init__(
        self,
        stt_engine,
        llm_engine: GeminiLLMEngine,
        tts_engine,
        max_context_messages: int = 10,
        enable_cache: bool = True,
    ):
        """
        Initialize the conversation manager.

        Args:
            stt_engine: Speech-to-Text engine
            llm_engine: Google Gemini LLM engine
            tts_engine: Text-to-Speech engine
            max_context_messages: Maximum number of messages to keep in context
            enable_cache: Whether to enable response caching
        """
        self.stt = stt_engine
        self.llm = llm_engine
        self.tts = tts_engine
        self.context = ConversationContext()
        self.max_context_messages = max_context_messages

        # Initialize response cache
        # Initialize response cache
        if enable_cache:
            # Check if LLM has data_store with embedder to share resources
            embedder = None
            if (
                hasattr(self.llm, "data_store")
                and self.llm.data_store
                and getattr(self.llm.data_store, "embedder", None)
            ):
                embedder = self.llm.data_store.embedder
                logger.info("Sharing existing embedder with ResponseCache")

            self.cache = ResponseCache(embedder=embedder)
            logger.info("Response caching enabled")
        else:
            self.cache = None

    def process_voice_query(
        self,
        audio_data: np.ndarray,
        preferred_language: Optional[str] = None,
        sample_rate: int = 16000,
    ) -> tuple[str, str, Optional[bytes]]:
        """
        Process a voice query end-to-end.

        Args:
            audio_data: Audio data as numpy array (float32)
            preferred_language: Preferred language ("en", "de", or None for auto-detect)
            sample_rate: Sample rate of the audio data (default: 16000)

        Returns:
            Tuple of (transcribed_text, response_text, audio_response)
        """
        # Step 1: Transcribe audio
        logger.info(f"Transcribing audio (sample_rate={sample_rate})...")
        transcribed_text, detected_language = self.stt.transcribe_sync(
            audio_data, language=preferred_language, sample_rate=sample_rate
        )

        if not transcribed_text:
            error_msg = {
                "en": "I didn't catch that. Could you please speak again?",
                "de": "Ich habe das nicht verstanden. Könnten Sie bitte wiederholen?",
            }
            lang = detected_language if detected_language in ["en", "de"] else "en"
            return "", error_msg[lang], self.tts.synthesize(error_msg[lang], lang)

        # Step 2: Generate response (text correction not needed with Google Cloud STT)
        logger.info("Generating response...")
        response_text = self._generate_response(transcribed_text, detected_language)
        logger.debug("Response generated. Updating context...")

        # Step 3: Update context
        try:
            self.context.add_message("user", transcribed_text, detected_language)
            self.context.add_message("assistant", response_text, detected_language)
            self._prune_context()
            logger.debug("Context updated.")
        except Exception as e:
            logger.error(f"Error updating context: {e}")

        # Step 4: Synthesize speech
        audio_response = None
        if self.tts:
            logger.info("Synthesizing speech...")
            try:
                # Clean text for TTS (remove markdown, etc.)
                clean_text = self._clean_text_for_tts(response_text)
                audio_response = self.tts.synthesize(clean_text, detected_language)
                logger.debug(
                    f"Speech synthesis returned {len(audio_response) if audio_response else 0} bytes"
                )
            except Exception as e:
                logger.error(f"Error in speech synthesis: {e}")
        else:
            logger.debug("TTS engine not available, skipping synthesis.")

        return transcribed_text, response_text, audio_response

    def process_text_query(
        self, text: str, language: str = "en"
    ) -> tuple[str, Optional[bytes]]:
        """
        Process a text query (no STT needed).

        Args:
            text: User's text query
            language: Language code ("en" or "de")

        Returns:
            Tuple of (response_text, audio_response)
        """
        if not text.strip():
            return "", None

        # Generate response
        logger.info(f"Processing text query ({language}): {text[:100]}...")
        response_text = self._generate_response(text, language)

        # Limit response length for TTS (max 1000 chars for faster speech)
        if len(response_text) > 1000:
            logger.warning(
                f"Response too long ({len(response_text)} chars), truncating for TTS"
            )
            response_text_for_tts = response_text[:1000] + "..."
        else:
            response_text_for_tts = response_text

        # Update context
        self.context.add_message("user", text, language)
        self.context.add_message("assistant", response_text, language)
        self._prune_context()

        # Synthesize speech (use truncated version if too long)
        audio_response = None
        if self.tts:
            try:
                # Clean text for TTS
                clean_text = self._clean_text_for_tts(response_text_for_tts)
                logger.info(
                    f"Synthesizing speech for response ({len(clean_text)} chars)..."
                )
                audio_response = self.tts.synthesize(clean_text, language)
                # Check if audio_response is valid (handle bytes or numpy array)
                has_audio = False
                if isinstance(audio_response, bytes):
                    has_audio = bool(audio_response)
                elif hasattr(audio_response, "size"):  # numpy array
                    has_audio = audio_response.size > 0

                if has_audio:
                    logger.info(
                        f"✓ Speech synthesis complete ({len(audio_response)} bytes)"
                    )
                else:
                    logger.warning("⚠ Speech synthesis returned None")
            except Exception as e:
                logger.error(f"Speech synthesis failed: {e}")
                audio_response = None

        return response_text, audio_response

    def _generate_response(self, query: str, language: str) -> str:
        """Generate response using LLM with caching."""
        import time

        start_time = time.time()

        # Check cache first
        if self.cache:
            cached_response = self.cache.get_cached_response(query, language)
            if cached_response:
                elapsed = time.time() - start_time
                logger.info(f"⚡ Cache hit! Response time: {elapsed * 1000:.1f}ms")
                return cached_response

        # Generate new response
        conversation_history = self.context.to_prompt_context(n=5)
        response = self.llm.generate_response(query, language, conversation_history)

        # Cache the response
        if self.cache and response:
            self.cache.cache_response(query, language, response)

        elapsed = time.time() - start_time
        logger.info(f"Generated new response in {elapsed:.2f}s")

        return response

    def _clean_text_for_tts(self, text: str) -> str:
        """
        Clean text for Text-to-Speech engine.
        Removes markdown formatting, links, and special characters.
        """
        # Remove bold/italic markers (*, **, _, __)
        text = re.sub(r"\*\*|__", "", text)  # Remove double markers
        text = re.sub(r"\*|_", "", text)  # Remove single markers

        # Remove links [text](url) -> text
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

        # Remove code blocks
        text = re.sub(r"```[\s\S]*?```", "", text)
        text = re.sub(r"`", "", text)

        # Remove bullet points (replace with comma for pause)
        text = re.sub(r"^\s*[-*]\s+", ", ", text, flags=re.MULTILINE)

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def _prune_context(self):
        """Prune conversation context to maximum size."""
        if len(self.context.messages) > self.max_context_messages * 2:
            # Keep only the most recent messages
            self.context.messages = self.context.messages[
                -(self.max_context_messages * 2) :
            ]
            logger.debug(f"Pruned context to {len(self.context.messages)} messages")

    def reset_context(self):
        """Reset conversation context."""
        self.context.clear()
        logger.info("Conversation context reset")

    def update_context(self, role: str, content: str, language: str = "en"):
        """Manually update context (used for restoring history)."""
        self.context.add_message(role, content, language)

    def get_conversation_history(self) -> list[dict]:
        """Get conversation history as list of dicts."""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "language": msg.language,
                "timestamp": msg.timestamp.isoformat(),
            }
            for msg in self.context.messages
        ]

    def export_conversation(self, filepath: str):
        """Export conversation history to JSON file."""
        import json

        history = self.get_conversation_history()

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            logger.info(f"Conversation exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export conversation: {e}")
