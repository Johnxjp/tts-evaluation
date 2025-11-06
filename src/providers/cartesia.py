"""Cartesia TTS provider implementation."""

import re
import requests
from src.providers.base import TTSProvider


class CartesiaProvider(TTSProvider):
    """Cartesia TTS provider."""

    API_ENDPOINT = "https://api.cartesia.ai/tts/bytes"
    API_VERSION = "2025-04-16"
    DEFAULT_MODEL = "sonic-3"
    DEFAULT_VOICE_ID = "c961b81c-a935-4c17-bfb3-ba2239de8c2f"  # Kyle
    DEFAULT_SAMPLE_RATE = 44100
    DEFAULT_FORMAT = "mp3"

    # Emotion mapping for Cartesia
    EMOTION_MAP = {
        "laughter": "laughter",
        "angry": "angry",
        "excited": "excited",
        "happy": "happy",
        "sad": "sad",
        "scared": "scared",
        "surprised": "surprised",
        "calm": "calm",
    }

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

    @property
    def can_emote(self) -> bool:
        """Return whether this provider supports emotions.

        Cartesia supports emotions only for sonic-3 class models.
        """
        return self.model.startswith("sonic-3")

    def _process_emotion_tags(self, text: str) -> str:
        """Process emotion tags into Cartesia format.

        Cartesia uses square brackets: [emotion]
        Replaces <tag>emotion</tag> with [emotion]

        Args:
            text: Text with emotion tags in format <tag>emotion</tag>

        Returns:
            Text formatted with Cartesia emotion markup, or text without tags if emotions not supported
        """
        if not self.can_emote:
            # Remove emotion tags if provider doesn't support emotions
            return re.sub(r"<tag>(.*?)</tag>", "", text).strip()

        # Replace <tag>emotion</tag> with [emotion] for supported emotions
        def replace_tag(match):
            emotion = match.group(1).strip().lower()
            if emotion in self.EMOTION_MAP and emotion == "laughter":
                return f"[{self.EMOTION_MAP[emotion]}]"
            elif emotion in self.EMOTION_MAP:
                return f'<emotion value="{self.EMOTION_MAP[emotion]}" />'
            return ""  # Remove unsupported emotion tags

        return re.sub(r"<tag>(.*?)</tag>", replace_tag, text).strip()

    def synthesize(self, text: str) -> bytes:
        """Synthesize speech using Cartesia API.

        Args:
            text: The text to convert to speech (may include emotion tags)

        Returns:
            Audio data as bytes

        Raises:
            Exception: If synthesis fails
        """
        # Process emotion tags
        text = self._process_emotion_tags(text)
        print(self.name, text)

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
