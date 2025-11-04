"""Hume TTS provider implementation."""

import base64
import requests
from src.providers.base import TTSProvider


class HumeProvider(TTSProvider):
    """Hume TTS provider."""

    API_ENDPOINT = "https://api.hume.ai/v0/tts"
    DEFAULT_FORMAT = "mp3"
    DEFAULT_VERSION = 2  # Octave 2
    DEFAULT_VOICE = "445d65ed-a87f-4140-9820-daf6d4f0a200"  # Booming American Narrator

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "Hume"

    def synthesize(self, text: str) -> bytes:
        """Synthesize speech using Hume API.

        Args:
            text: The text to convert to speech

        Returns:
            Audio data as bytes (MP3 format)

        Raises:
            Exception: If synthesis fails
        """
        headers = {
            "X-Hume-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "utterances": [
                {
                    "text": text,
                    "voice": {
                        "VoicedId": {"id": self.DEFAULT_VOICE},
                        "VoiceName": {"name": "Booming American Narrator"},
                    },
                }
            ],
            "format": self.DEFAULT_FORMAT,
            "version": self.DEFAULT_VERSION,
        }

        response = requests.post(
            self.API_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.status_code != 200:
            raise Exception(f"Hume API error: {response.status_code} - {response.text}")

        response_data = response.json()

        # Extract audio from the first generation
        if not response_data or len(response_data) == 0:
            raise Exception("No generations in Hume response")

        first_generation = response_data[0]
        audio_b64 = first_generation.get("audio")

        if not audio_b64:
            raise Exception("No audio data in Hume response")

        return base64.b64decode(audio_b64)
