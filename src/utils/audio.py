"""Audio utilities for handling TTS audio data."""

import tempfile
import os
import uuid
import json
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime


def save_audio_temp(audio_data: bytes, format: str = "mp3") -> str:
    """Save audio data to a temporary file.

    Args:
        audio_data: Raw audio bytes
        format: Audio format (mp3, wav, etc.)

    Returns:
        Path to the temporary file
    """
    suffix = f".{format}"
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.write(audio_data)
    temp_file.close()
    return temp_file.name


def cleanup_temp_file(file_path: str) -> None:
    """Remove a temporary audio file.

    Args:
        file_path: Path to the file to remove
    """
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception:
        pass  # Silently ignore cleanup errors


def get_audio_format(audio_data: bytes) -> Optional[str]:
    """Detect audio format from the file header.

    Args:
        audio_data: Raw audio bytes

    Returns:
        Detected format ('mp3', 'wav', etc.) or None if unknown
    """
    if audio_data.startswith(b"RIFF") and b"WAVE" in audio_data[:12]:
        return "wav"
    elif audio_data.startswith(b"ID3") or audio_data.startswith(b"\xff\xfb"):
        return "mp3"
    return None


def create_request_folder(text: str, provider_settings: List[Dict[str, Any]], base_path: Path = None) -> Tuple[str, Path]:
    """Create a unique folder for a TTS request.

    Args:
        text: The text content of the request
        provider_settings: List of provider settings dictionaries
        base_path: Base directory for data storage (default: ./data)

    Returns:
        Tuple of (request_uuid, folder_path)
    """
    if base_path is None:
        base_path = Path.cwd() / "data"

    # Generate UUID for this request
    request_uuid = str(uuid.uuid4())

    # Create subfolder
    request_folder = base_path / request_uuid
    request_folder.mkdir(parents=True, exist_ok=True)

    # Save request as JSON
    request_file = request_folder / "request.json"
    timestamp = datetime.now().isoformat()

    request_data = {
        "timestamp": timestamp,
        "uuid": request_uuid,
        "text": text,
        "provider_settings": provider_settings,
    }

    with open(request_file, "w", encoding="utf-8") as f:
        json.dump(request_data, f, indent=2, ensure_ascii=False)

    return request_uuid, request_folder


def save_audio_permanent(
    audio_data: bytes,
    provider_name: str,
    audio_format: str,
    request_folder: Path,
) -> Path:
    """Save audio data permanently in the request folder.

    Args:
        audio_data: Raw audio bytes
        provider_name: Name of the TTS provider
        audio_format: Audio format (mp3, wav, etc.)
        request_folder: Path to the request folder

    Returns:
        Path to the saved audio file
    """
    # Sanitize provider name for filename
    safe_provider_name = provider_name.lower().replace(" ", "_")
    filename = f"{safe_provider_name}.{audio_format}"

    audio_file = request_folder / filename
    with open(audio_file, "wb") as f:
        f.write(audio_data)

    return audio_file
