"""Inworld AI TTS provider implementation."""

import base64
import requests
from src.providers.base import TTSProvider


class InworldProvider(TTSProvider):
    """Inworld AI TTS provider."""

    API_ENDPOINT = "https://api.inworld.ai/tts/v1/voice"
    DEFAULT_VOICE_ID = "Alex"
    DEFAULT_MODEL_ID = "inworld-tts-1"
    DEFAULT_SAMPLE_RATE = "44100"
    DEFAULT_FORMAT = "MP3"

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "Inworld AI"

    def synthesize(self, text: str) -> bytes:
        """Synthesize speech using Inworld AI API.

        Args:
            text: The text to convert to speech

        Returns:
            Audio data as bytes (MP3 format)

        Raises:
            Exception: If synthesis fails
        """
        headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "text": text,
            "voiceId": self.DEFAULT_VOICE_ID,
            "modelId": self.DEFAULT_MODEL_ID,
            "audioConfig": {
                "audioEncoding": self.DEFAULT_FORMAT,
                "sampleRateHertz": self.DEFAULT_SAMPLE_RATE,
            },
        }

        response = requests.post(
            self.API_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.status_code != 200:
            raise Exception(f"Inworld API error: {response.status_code} - {response.text}")

        response_data = response.json()

        # Decode base64 audio content
        audio_content_b64 = response_data.get("audioContent")
        if not audio_content_b64:
            raise Exception("No audio content in Inworld response")

        return base64.b64decode(audio_content_b64)
