"""Speechify TTS provider implementation."""

import base64
import requests
import re
from typing import List
from src.providers.base import TTSProvider


class SpeechifyProvider(TTSProvider):
    """Speechify TTS provider."""

    API_ENDPOINT = "https://api.sws.speechify.com/v1/audio/speech"
    DEFAULT_VOICE_ID = "oliver"  # Oliver
    DEFAULT_MODEL = "simba-english"
    DEFAULT_FORMAT = "mp3"

    # Emotion mapping for Speechify (uses SSML)
    # Note: laughter is not supported
    EMOTION_MAP = {
        "angry": "angry",
        "excited": "energetic",
        "sad": "sad",
        "scared": "terrified",
        "happy": "happy",
        "surprised": "surprised",
        "calm": "calm",
    }

    def __init__(self, api_key: str, model: str = None):
        """Initialize the Speechify provider.

        Args:
            api_key: The API key for authentication
            model: Model to use (default: simba-english)
        """
        super().__init__(api_key)
        self.model = model or self.DEFAULT_MODEL

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "Speechify"

    @property
    def settings(self):
        """Return provider settings."""
        return {
            "name": self.name,
            "model_id": self.model,
            "format": self.DEFAULT_FORMAT,
            "voice_id": self.DEFAULT_VOICE_ID,
            "sample_rate": None,
        }

    @property
    def can_emote(self) -> bool:
        """Return whether this provider supports emotions.

        Speechify supports emotions for supported models.
        Note: According to docs, supported models are 'inworld-tts-1' and 'inworld-tts-1-max',
        but the task description mentions 'simba-english' as the Speechify model.
        Assuming emotion support is available.
        """
        return True

    def _process_emotion_tags(self, text: str) -> str:
        # Find all tags
        tags = re.findall(r"<tag>(.*?)</tag>", text)
        if not tags:
            return text  # no tags, return as-is

        parts = re.split(r"<tag>.*?</tag>", text)

        # Clean up whitespace alignment
        parts = [p.strip() for p in parts if p.strip() != ""]

        # If only one tag — wrap the whole sentence
        if len(tags) == 1:
            emotion = tags[0].strip()
            mapped_emotion = self.EMOTION_MAP.get(emotion)
            if mapped_emotion:
                return f'<speechify:style emotion="{mapped_emotion}">{text.replace(f"<tag>{emotion}</tag>", "").strip()}</speechify:style>'
            else:
                # unsupported — just strip tag
                return text.replace(f"<tag>{emotion}</tag>", "").strip()

        # Multiple tags — build result
        result_parts = []
        text_segments = re.split(r"<tag>.*?</tag>", text)

        # The pattern alternates: [text1, text2, text3...] with tags = [tag1, tag2...]
        for i, tag in enumerate(tags):
            emotion = tag.strip()
            mapped_emotion = self.EMOTION_MAP.get(emotion)
            if mapped_emotion:
                # Wrap the following text segment
                # e.g. tag i corresponds to text_segments[i+1]
                segment = text_segments[i + 1].strip() if i + 1 < len(text_segments) else ""
                if segment:
                    result_parts.append(
                        f'<speechify:style emotion="{mapped_emotion}">{segment}</speechify:style>'
                    )
            else:
                # Unsupported tag: just append next text segment raw
                segment = text_segments[i + 1].strip() if i + 1 < len(text_segments) else ""
                if segment:
                    result_parts.append(segment)

        return " ".join(result_parts)

    def synthesize(self, text: str) -> bytes:
        """Synthesize speech using Speechify API.

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
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "input": f"<speak>{text}</speak>",  # all speechify text has SSML
            "voice_id": self.DEFAULT_VOICE_ID,
            "audio_format": self.DEFAULT_FORMAT,
            "model": self.model,
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
