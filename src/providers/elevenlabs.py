"""ElevenLabs TTS provider implementation."""

import requests
from src.providers.base import TTSProvider


class ElevenLabsProvider(TTSProvider):
    """ElevenLabs TTS provider."""

    API_ENDPOINT_TEMPLATE = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    DEFAULT_VOICE_ID = "nPczCjzI2devNBz1zQrb"  # Brian
    DEFAULT_MODEL_ID = "eleven_v3"  # or eleven_flash_v2_5
    DEFAULT_FORMAT = "mp3"
    DEFAULT_SAMPLE_RATE = 44100
    DEFAULT_BIT_RATE = 128

    def __init__(self, api_key: str, model: str = None):
        """Initialize the ElevenLabs provider.

        Args:
            api_key: The API key for authentication
            model: Model to use (default: eleven_v3)
        """
        super().__init__(api_key)
        self.model = model or self.DEFAULT_MODEL_ID

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "ElevenLabs"

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
        """Synthesize speech using ElevenLabs API.

        Args:
            text: The text to convert to speech

        Returns:
            Audio data as bytes (MP3 format)

        Raises:
            Exception: If synthesis fails
        """
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "text": text,
            "model_id": self.model,
        }

        output_format = f"{self.DEFAULT_FORMAT}_{self.DEFAULT_SAMPLE_RATE}_{self.DEFAULT_BIT_RATE}"
        url = self.API_ENDPOINT_TEMPLATE.format(voice_id=self.DEFAULT_VOICE_ID)
        params = {"output_format": output_format}

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            params=params,
            timeout=30,
        )

        if response.status_code != 200:
            raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")

        return response.content
