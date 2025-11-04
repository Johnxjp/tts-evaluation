"""ElevenLabs TTS provider implementation."""

import requests
from src.providers.base import TTSProvider


class ElevenLabsProvider(TTSProvider):
    """ElevenLabs TTS provider."""

    API_ENDPOINT_TEMPLATE = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    DEFAULT_VOICE_ID = "nPczCjzI2devNBz1zQrb"  # Brian
    DEFAULT_MODEL_ID = "eleven_flash_v2_5"
    DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"

    def __init__(self, api_key: str):
        """Initialize the ElevenLabs provider.

        Args:
            api_key: The API key for authentication
            voice_id: Voice ID to use (default: Rachel)
        """
        super().__init__(api_key)

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "ElevenLabs"

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
            "model_id": self.DEFAULT_MODEL_ID,
        }

        url = self.API_ENDPOINT_TEMPLATE.format(voice_id=self.DEFAULT_VOICE_ID)
        params = {"output_format": self.DEFAULT_OUTPUT_FORMAT}

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
