"""Base class for TTS providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class TTSProvider(ABC):
    """Abstract base class for TTS providers."""

    def __init__(self, api_key: str):
        """Initialize the provider with an API key.

        Args:
            api_key: The API key for authentication
        """
        self.api_key = api_key

    @abstractmethod
    def synthesize(self, text: str) -> bytes:
        """Synthesize speech from text.

        Text may contain emotion tags in format <tag>emotion</tag>.
        Each provider will process these tags according to their API requirements.

        Args:
            text: The text to convert to speech (may include emotion tags)

        Returns:
            Audio data as bytes (WAV or MP3 format)

        Raises:
            Exception: If synthesis fails
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        pass

    @property
    @abstractmethod
    def settings(self) -> Dict[str, Any]:
        """Return provider settings as a dictionary.

        Returns:
            Dictionary with keys: name, model_id, format, voice_id, sample_rate
        """
        pass

    @property
    @abstractmethod
    def can_emote(self) -> bool:
        """Return whether this provider/model supports emotion tags.

        Returns:
            True if provider supports emotions, False otherwise
        """
        pass

    def validate_api_key(self) -> bool:
        """Validate that the API key is set.

        Returns:
            True if API key is valid, False otherwise
        """
        return bool(self.api_key and self.api_key.strip())
