"""Inworld AI TTS provider implementation."""

import re
import base64
import requests
from src.providers.base import TTSProvider


class InworldProvider(TTSProvider):
    """Inworld AI TTS provider."""

    API_ENDPOINT = "https://api.inworld.ai/tts/v1/voice"
    DEFAULT_VOICE_ID = "Alex"
    DEFAULT_MODEL_ID = "inworld-tts-1"
    DEFAULT_SAMPLE_RATE = 44100
    DEFAULT_FORMAT = "MP3"

    # Emotion mapping for Inworld AI
    EMOTION_MAP = {
        "laughter": "laughing",
        "angry": "angry",
        "excited": "happy",
        "sad": "sad",
        "scared": "fearful",
    }

    def __init__(self, api_key: str, model: str = None):
        """Initialize the Inworld provider.

        Args:
            api_key: The API key for authentication
            model: Model to use (default: inworld-tts-1)
        """
        super().__init__(api_key)
        self.model = model or self.DEFAULT_MODEL_ID

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "Inworld AI"

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

        Inworld AI supports emotions for both models.
        """
        return True

    def _process_emotion_tags(self, text: str) -> str:
        """Process emotion tags into Inworld AI format.

        Inworld AI uses square brackets: [emotion]
        Replaces <tag>emotion</tag> with [emotion]

        Args:
            text: Text with emotion tags in format <tag>emotion</tag>

        Returns:
            Text formatted with Inworld AI emotion markup
        """
        # Replace <tag>emotion</tag> with [emotion] for supported emotions
        def replace_tag(match):
            emotion = match.group(1).strip().lower()
            if emotion in self.EMOTION_MAP:
                return f"[{self.EMOTION_MAP[emotion]}]"
            return ""  # Remove unsupported emotion tags

        return re.sub(r'<tag>(.*?)</tag>', replace_tag, text).strip()

    def synthesize(self, text: str) -> bytes:
        """Synthesize speech using Inworld AI API.

        Args:
            text: The text to convert to speech (may include emotion tags)

        Returns:
            Audio data as bytes (MP3 format)

        Raises:
            Exception: If synthesis fails
        """
        # Process emotion tags
        processed_text = self._process_emotion_tags(text)

        headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "text": processed_text,
            "voiceId": self.DEFAULT_VOICE_ID,
            "modelId": self.model,
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
