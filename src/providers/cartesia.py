"""Cartesia TTS provider implementation."""

import requests
from src.providers.base import TTSProvider


class CartesiaProvider(TTSProvider):
    """Cartesia TTS provider."""

    API_ENDPOINT = "https://api.cartesia.ai/tts/bytes"
    API_VERSION = "2025-04-16"
    DEFAULT_MODEL = "sonic-3"
    DEFAULT_VOICE_ID = "228fca29-3a0a-435c-8728-5cb483251068"  # Kiefer
    DEFAULT_SAMPLE_RATE = 44100
    DEFAULT_FORMAT = "mp3"

    def __init__(self, api_key: str, model: str = None):
        """Initialize the Cartesia provider.

        Args:
            api_key: The API key for authentication
            model: Model to use (default: sonic-3)
        """
        super().__init__(api_key)
        self.model = model or self.DEFAULT_MODEL

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "Cartesia"

    @property
    def settings(self):
        """Return provider settings."""
        return {
            "name": self.name,
            "model_id": self.model,
            "format": self.DEFAULT_FORMAT,
            "voice_id": self.DEFAULT_VOICE_ID,
            "sample_rate": self.DEFAULT_SAMPLE_RATE,
        }

    def synthesize(self, text: str) -> bytes:
        """Synthesize speech using Cartesia API.

        Args:
            text: The text to convert to speech

        Returns:
            Audio data as bytes

        Raises:
            Exception: If synthesis fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Cartesia-Version": self.API_VERSION,
            "Content-Type": "application/json",
        }

        payload = {
            "model_id": self.model,
            "transcript": text,
            "voice": {
                "mode": "id",
                "id": self.DEFAULT_VOICE_ID,
            },
            "language": "en",
            "output_format": {
                "container": self.DEFAULT_FORMAT,
                "bit_rate": 128000,
                "sample_rate": self.DEFAULT_SAMPLE_RATE,
            },
        }

        response = requests.post(
            self.API_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.status_code != 200:
            raise Exception(f"Cartesia API error: {response.status_code} - {response.text}")

        return response.content
