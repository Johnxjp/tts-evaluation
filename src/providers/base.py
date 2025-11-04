"""Base class for TTS providers."""

from abc import ABC, abstractmethod


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

        Args:
            text: The text to convert to speech

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

    def validate_api_key(self) -> bool:
        """Validate that the API key is set.

        Returns:
            True if API key is valid, False otherwise
        """
        return bool(self.api_key and self.api_key.strip())
