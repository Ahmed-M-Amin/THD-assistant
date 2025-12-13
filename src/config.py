"""Configuration management using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    # API Keys
    GEMINI_API_KEY: str

    # Gemini LLM Settings
    GEMINI_MODEL_NAME: str = "gemini-1.5-flash"

    # Performance settings
    MAX_CONTEXT_MESSAGES: int = 10
    LLM_MAX_TOKENS: int = 1024  # Increased for API models
    LLM_TEMPERATURE: float = 0.7

    # Audio settings
    SAMPLE_RATE: int = 16000
    RECORDING_DURATION: int = 5
    AUDIO_INPUT_DEVICE: str = (
        ""  # Empty = default, or device number from list_microphones.py
    )
    TTS_VOICE_PREFERENCE: str = "female"  # Options: "female", "male" (for edge-tts); "zira", "hazel" (for pyttsx3)
    TTS_ENGINE: str = "edge-tts"  # Options: "edge-tts", "gtts", "pyttsx3", "dummy"

    # Data paths
    PROGRAMS_DATA_PATH: str = "data/programs"
    CONFIG_PATH: str = "config/content_index.yaml"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Response Caching
    ENABLE_RESPONSE_CACHE: bool = True
    CACHE_TTL: int = 3600  # 1 hour
    MAX_CACHE_SIZE: int = 1000
    CACHE_SIMILARITY_THRESHOLD: float = 0.85

    def validate_paths(self) -> list[str]:
        """Validate that required paths exist."""
        errors = []

        # Check data directory
        if not Path(self.PROGRAMS_DATA_PATH).exists():
            errors.append(f"Programs data path not found: {self.PROGRAMS_DATA_PATH}")

        # Check config file
        if not Path(self.CONFIG_PATH).exists():
            errors.append(f"Config file not found: {self.CONFIG_PATH}")

        return errors

    # validate_models is no longer needed as we are using API-based models


# Global settings instance
settings = Settings()
