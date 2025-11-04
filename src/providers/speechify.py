"""Speechify TTS provider implementation."""

import base64
import requests
from src.providers.base import TTSProvider


class SpeechifyProvider(TTSProvider):
    """Speechify TTS provider."""

    API_ENDPOINT = "https://api.sws.speechify.com/v1/audio/speech"
    DEFAULT_VOICE_ID = "oliver"  # Oliver
    DEFAULT_MODEL = "simba-english"
    DEFAULT_FORMAT = "mp3"

    def __init__(self, api_key: str):
        """Initialize the Speechify provider.

        Args:
            api_key: The API key for authentication
            voice_id: Voice ID to use (default: henry)
        """
        super().__init__(api_key)

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "Speechify"

    def synthesize(self, text: str) -> bytes:
        """Synthesize speech using Speechify API.

        Args:
            text: The text to convert to speech

        Returns:
            Audio data as bytes (MP3 format)

        Raises:
            Exception: If synthesis fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "input": text,
            "voice_id": self.DEFAULT_VOICE_ID,
            "audio_format": self.DEFAULT_FORMAT,
            "model": self.DEFAULT_MODEL,
        }

        response = requests.post(
            self.API_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.status_code != 200:
            raise Exception(f"Speechify API error: {response.status_code} - {response.text}")

        response_data = response.json()

        # Decode base64 audio data
        audio_data_b64 = response_data.get("audio_data")
        if not audio_data_b64:
            raise Exception("No audio data in Speechify response")

        return base64.b64decode(audio_data_b64)
