"""ElevenLabs TTS provider implementation."""

import re
import requests
from src.providers.base import TTSProvider


class ElevenLabsProvider(TTSProvider):
    """ElevenLabs TTS provider."""

    API_ENDPOINT_TEMPLATE = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    DEFAULT_VOICE_ID = "1SM7GgM6IMuvQlz2BwM3"  # Mark
    DEFAULT_MODEL_ID = "eleven_v3"  # or eleven_flash_v2_5
    DEFAULT_FORMAT = "mp3"
    DEFAULT_SAMPLE_RATE = 44100
    DEFAULT_BIT_RATE = 128

    # Emotion mapping for ElevenLabs
    EMOTION_MAP = {
        "laughter": "laughter",
        "angry": "angry",
        "excited": "excited",
        "happy": "happy",
        "sad": "sad",
        "surprised": "surprised",
        "scared": "scared",
        "calm": "calm",
    }

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

    @property
    def can_emote(self) -> bool:
        """Return whether this provider supports emotions.

        ElevenLabs supports emotions only for eleven_v3 model.
        """
        return self.model == "eleven_v3"

    def _process_emotion_tags(self, text: str) -> str:
        """Process emotion tags into ElevenLabs format.

        ElevenLabs uses square brackets: [emotion]
        Replaces <tag>emotion</tag> with [emotion]

        Args:
            text: Text with emotion tags in format <tag>emotion</tag>

        Returns:
            Text formatted with ElevenLabs emotion markup, or text without tags if emotions not supported
        """
        if not self.can_emote:
            # Remove emotion tags if provider doesn't support emotions
            return re.sub(r"<tag>(.*?)</tag>", "", text).strip()

        # Replace <tag>emotion</tag> with [emotion] for supported emotions
        def replace_tag(match):
            emotion = match.group(1).strip().lower()
            if emotion in self.EMOTION_MAP:
                return f"[{self.EMOTION_MAP[emotion]}]"
            return ""  # Remove unsupported emotion tags

        return re.sub(r"<tag>(.*?)</tag>", replace_tag, text).strip()

    def synthesize(self, text: str) -> bytes:
        """Synthesize speech using ElevenLabs API.

        Args:
            text: The text to convert to speech

        Returns:
            Audio data as bytes (MP3 format)

        Raises:
            Exception: If synthesis fails
        """

        text = self._process_emotion_tags(text)
        print(self.name, text)
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
            timeout=60,
        )

        if response.status_code != 200:
            raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")

        return response.content
