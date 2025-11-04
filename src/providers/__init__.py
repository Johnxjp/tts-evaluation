"""TTS provider registry and initialization."""

import os
from typing import Dict, Optional
from .base import TTSProvider
from .cartesia import CartesiaProvider
from .inworld import InworldProvider
from .elevenlabs import ElevenLabsProvider
from .hume import HumeProvider
from .speechify import SpeechifyProvider


def create_providers(
    cartesia_key: Optional[str] = None,
    inworld_key: Optional[str] = None,
    elevenlabs_key: Optional[str] = None,
    hume_key: Optional[str] = None,
    speechify_key: Optional[str] = None,
) -> Dict[str, TTSProvider]:
    """Create and initialize all TTS providers.

    Args:
        cartesia_key: Cartesia API key
        inworld_key: Inworld AI API key
        elevenlabs_key: ElevenLabs API key
        hume_key: Hume API key
        speechify_key: Speechify API key

    Returns:
        Dictionary mapping provider names to provider instances
    """
    providers = {}

    if cartesia_key:
        providers["Cartesia"] = CartesiaProvider(cartesia_key)

    if inworld_key:
        providers["Inworld AI"] = InworldProvider(inworld_key)

    if elevenlabs_key:
        providers["ElevenLabs"] = ElevenLabsProvider(elevenlabs_key)

    if hume_key:
        providers["Hume"] = HumeProvider(hume_key)

    if speechify_key:
        providers["Speechify"] = SpeechifyProvider(speechify_key)

    return providers


def load_providers_from_env() -> Dict[str, TTSProvider]:
    """Load providers using API keys from environment variables.

    Returns:
        Dictionary mapping provider names to provider instances
    """
    return create_providers(
        cartesia_key=os.getenv("CARTESIA_API_KEY"),
        inworld_key=os.getenv("INWORLD_API_KEY"),
        elevenlabs_key=os.getenv("ELEVENLABS_API_KEY"),
        hume_key=os.getenv("HUME_API_KEY"),
        speechify_key=os.getenv("SPEECHIFY_API_KEY"),
    )


__all__ = [
    "TTSProvider",
    "CartesiaProvider",
    "InworldProvider",
    "ElevenLabsProvider",
    "HumeProvider",
    "SpeechifyProvider",
    "create_providers",
    "load_providers_from_env",
]
