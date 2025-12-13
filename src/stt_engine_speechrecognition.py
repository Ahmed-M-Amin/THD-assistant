"""Speech-to-Text engine using the SpeechRecognition library."""

import logging
import speech_recognition as sr
import numpy as np

logger = logging.getLogger(__name__)


class SpeechRecognitionSTTEngine:
    """
    Speech-to-Text engine utilizing the SpeechRecognition library
    with Google Web Speech API for transcription.
    """

    def __init__(
        self,
        audio_device: int = None,
        sample_rate: int = 16000,
        preferred_language: str = "en",
    ):
        """
        Initialize the SpeechRecognition STT engine.

        Args:
            audio_device: Index of the audio input device to use.
            sample_rate: Sample rate for audio recording.
            preferred_language: Preferred language code ('en' or 'de').
        """
        self.recognizer = sr.Recognizer()
        self.audio_device = audio_device
        self.sample_rate = sample_rate
        self.preferred_language = preferred_language

        # Enable dynamic energy threshold for better adaptability
        self.recognizer.dynamic_energy_threshold = True

        # Map language codes to Google Speech API locale codes
        self.language_map = {"en": "en-US", "de": "de-DE"}

        logger.info(
            f"SpeechRecognition STT engine initialized. Audio Device: {self.audio_device}, Sample Rate: {self.sample_rate}, Language: {self.preferred_language}"
        )

    def transcribe(self) -> str:
        """
        Listen for speech and transcribe it using Google Web Speech API.

        Returns:
            Transcribed text, or an empty string if no speech is detected or an error occurs.
        """
        # Get the correct language code for Google Speech API
        google_language = self.language_map.get(self.preferred_language, "en-US")

        with sr.Microphone(
            device_index=self.audio_device, sample_rate=self.sample_rate
        ) as source:
            self.recognizer.adjust_for_ambient_noise(source)
            logger.info(f"Listening for speech... (language: {google_language})")
            try:
                audio = self.recognizer.listen(source)
                logger.info("Speech detected, transcribing...")
                text = self.recognizer.recognize_google(audio, language=google_language)
                logger.debug(f"Transcribed: {text}")
                return text
            except sr.UnknownValueError:
                logger.warning("Google Speech Recognition could not understand audio")
                return ""
            except sr.RequestError as e:
                logger.error(
                    f"Could not request results from Google Speech Recognition service; {e}"
                )
                return ""
            except Exception as e:
                logger.error(f"An unexpected error occurred during transcription: {e}")
                return ""

    def transcribe_audio_data(
        self, audio_data: np.ndarray, sample_rate: int, language: str = "en"
    ) -> str:
        """
        Transcribe pre-recorded audio data.

        Args:
            audio_data: NumPy array of audio data (float32).
            sample_rate: Sample rate of the audio data.
            language: Language code for transcription.

        Returns:
            Transcribed text, or an empty string if no speech is detected or an error occurs.
        """
        # Get the correct language code for Google Speech API
        google_language = self.language_map.get(language, "en-US")

        # Handle stereo audio - convert to mono by averaging channels
        if len(audio_data.shape) > 1 and audio_data.shape[1] > 1:
            logger.info(f"Converting stereo audio to mono (shape: {audio_data.shape})")
            audio_data = np.mean(audio_data, axis=1)

        # Ensure audio is 1D
        audio_data = audio_data.flatten()

        # NORMALIZE AUDIO - boost quiet recordings for better transcription
        max_amplitude = np.max(np.abs(audio_data))
        if max_amplitude > 0 and max_amplitude < 0.5:
            # Audio is too quiet, normalize to 0.8 max amplitude
            normalization_factor = 0.8 / max_amplitude
            audio_data = audio_data * normalization_factor
            audio_data = np.clip(audio_data, -1.0, 1.0)
            logger.info(
                f"🔊 Audio normalized: {max_amplitude:.4f} → 0.8 (factor: {normalization_factor:.1f}x)"
            )

        # Convert numpy array to SpeechRecognition AudioData format
        # Check if audio is already int16 or needs conversion from float32
        if audio_data.dtype == np.int16:
            audio_data_int16 = audio_data
        else:
            # Assume float32 in range [-1.0, 1.0], convert to int16
            audio_data_int16 = (audio_data * 32767).astype(np.int16)

        audio = sr.AudioData(
            audio_data_int16.tobytes(), sample_rate, 2
        )  # 2 bytes per sample for int16

        logger.info(
            f"Transcribing pre-recorded audio (sample_rate={sample_rate}, language={google_language})..."
        )
        logger.info(
            f"Audio data shape: {audio_data.shape}, dtype: {audio_data.dtype}, min: {audio_data.min():.4f}, max: {audio_data.max():.4f}, samples: {len(audio_data)}"
        )

        try:
            text = self.recognizer.recognize_google(audio, language=google_language)
            logger.info(f"✓ Transcribed successfully: {text}")
            return text
        except sr.UnknownValueError:
            logger.warning(
                "⚠ Google Speech Recognition could not understand audio - audio may be too quiet, unclear, or contain no speech"
            )
            return ""
        except sr.RequestError as e:
            logger.error(
                f"Could not request results from Google Speech Recognition service; {e}"
            )
            return ""
        except Exception as e:
            logger.error(f"An unexpected error occurred during transcription: {e}")
            return ""

    def transcribe_sync(
        self, audio_data: np.ndarray, language: str = "en", sample_rate: int = 16000
    ) -> tuple[str, str]:
        """
        Synchronous transcription method compatible with ConversationManager.

        Args:
            audio_data: Audio data as numpy array.
            language: Preferred language code.
            sample_rate: Sample rate of the audio data (default: 16000).

        Returns:
            Tuple of (transcribed_text, detected_language).
        """
        text = self.transcribe_audio_data(
            audio_data, sample_rate=sample_rate, language=language
        )
        return text, language
