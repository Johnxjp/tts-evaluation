"""Hume TTS provider implementation."""

import base64
import requests
from src.providers.base import TTSProvider


class HumeProvider(TTSProvider):
    """Hume TTS provider."""

    API_ENDPOINT = "https://api.hume.ai/v0/tts"
    DEFAULT_FORMAT = "mp3"
    DEFAULT_VERSION = "2"  # Octave 2
    DEFAULT_VOICE_ID = "445d65ed-a87f-4140-9820-daf6d4f0a200"  # Booming American Narrator

    def __init__(self, api_key: str, model: str = None):
        """Initialize the Hume provider.

        Args:
            api_key: The API key for authentication
            model: Model version to use - '1' or '2' (default: '2')
        """
        super().__init__(api_key)
        self.model = model or self.DEFAULT_VERSION

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

        Example request format
        curl -X POST https://api.hume.ai/v0/tts \
            -H "X-Hume-Api-Key: <apiKey>" \
            -H "Content-Type: application/json" \
            -d '{
        "utterances": [
            {
            "text": "Beauty is no quality in things themselves: It exists merely in the mind which contemplates them.",
            "description": "Middle-aged masculine voice with a clear, rhythmic Scots lilt, rounded vowels, and a warm, steady tone with an articulate, academic quality."
            }
        ],
        "context": {
            "utterances": [
            {
                "text": "How can people see beauty so differently?",
                "description": "A curious student with a clear and respectful tone, seeking clarification on Hume\'s ideas with a straightforward question."
            }
            ]
        },
        "format": {
            "type": "mp3"
        },
        "num_generations": 1,
        "version": "2"
        }'
        
        """
        headers = {
            "X-Hume-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

        # Do not change the Payload format
        payload = {
            "utterances": [{"text": text, "voice": {"id": self.DEFAULT_VOICE_ID}}],
            "format": {"type": self.DEFAULT_FORMAT},
            "version": self.model,
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

        # Extract audio from generations[0].audio
        if "generations" not in response_data or len(response_data["generations"]) == 0:
            raise Exception("No generations in Hume response")

        first_generation = response_data["generations"][0]
        audio_b64 = first_generation.get("audio")

        if not audio_b64:
            raise Exception("No audio data in Hume response")

        return base64.b64decode(audio_b64)
