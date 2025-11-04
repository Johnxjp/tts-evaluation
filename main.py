"""Main Streamlit application for TTS evaluation."""

import os
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

from src.providers import create_providers
from src.utils.audio import (
    save_audio_temp,
    get_audio_format,
    create_request_folder,
    save_audio_permanent,
)

# Load environment variables
load_dotenv()

# Model options for each provider
MODEL_OPTIONS = {
    "Cartesia": ["sonic-3", "sonic-2"],
    "ElevenLabs": ["eleven_v3", "eleven_flash_v2_5"],
    "Inworld AI": ["inworld-tts-1", "inworld-tts-1-max"],
    "Hume": ["2", "1"],
    "Speechify": ["simba-english"],
}


def get_generation_history(limit=5):
    """Get the last N generations from the data folder.

    Args:
        limit: Maximum number of generations to retrieve

    Returns:
        List of tuples (uuid, folder_path, timestamp, text) sorted by newest first
    """
    data_dir = Path.cwd() / "data"
    if not data_dir.exists():
        return []

    generations = []
    for folder in data_dir.iterdir():
        if folder.is_dir():
            request_file = folder / "request.txt"
            if request_file.exists():
                try:
                    with open(request_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        timestamp = None
                        text = ""

                        # Parse request.txt
                        for i, line in enumerate(lines):
                            if line.startswith("Timestamp:"):
                                timestamp_str = line.replace("Timestamp:", "").strip()
                                timestamp = datetime.fromisoformat(timestamp_str)
                            elif i >= 3:  # Text starts after line 3
                                text += line

                        text = text.strip()
                        generations.append((folder.name, folder, timestamp, text))
                except Exception:
                    continue

    # Sort by timestamp (newest first)
    generations.sort(key=lambda x: x[2] if x[2] else datetime.min, reverse=True)

    return generations[:limit]


def main():
    """Run the Streamlit TTS evaluation application."""
    st.set_page_config(
        page_title="TTS Evaluation Tool",
        page_icon="🎙️",
        layout="wide",
    )

    st.title("🎙️ Text-to-Speech Evaluation Tool")
    st.markdown("Compare the quality of different text-to-speech services side-by-side.")

    # Model Selection Toolbar
    st.markdown("---")
    st.subheader("⚙️ Model Settings")

    # Get API keys
    api_keys = {
        "cartesia": os.getenv("CARTESIA_API_KEY"),
        "inworld": os.getenv("INWORLD_API_KEY"),
        "elevenlabs": os.getenv("ELEVENLABS_API_KEY"),
        "hume": os.getenv("HUME_API_KEY"),
        "speechify": os.getenv("SPEECHIFY_API_KEY"),
    }

    # Check if any providers are configured
    if not any(api_keys.values()):
        st.error("⚠️ No TTS providers configured. Please set up your API keys in the .env file.")
        st.info(
            """
            Required environment variables:
            - CARTESIA_API_KEY
            - INWORLD_API_KEY
            - ELEVENLABS_API_KEY
            - HUME_API_KEY
            - SPEECHIFY_API_KEY
            """
        )
        return

    # Create columns for model selection
    available_providers = []
    if api_keys["cartesia"]:
        available_providers.append("Cartesia")
    if api_keys["elevenlabs"]:
        available_providers.append("ElevenLabs")
    if api_keys["inworld"]:
        available_providers.append("Inworld AI")
    if api_keys["hume"]:
        available_providers.append("Hume")
    if api_keys["speechify"]:
        available_providers.append("Speechify")

    num_providers = len(available_providers)
    cols = st.columns(num_providers)

    # Store selected models
    selected_models = {}

    for idx, provider_name in enumerate(available_providers):
        with cols[idx]:
            options = MODEL_OPTIONS.get(provider_name, [])
            if options:
                if len(options) == 1:
                    st.markdown(f"**{provider_name}**")
                    st.text(options[0])
                    selected_models[provider_name] = options[0]
                else:
                    selected_models[provider_name] = st.selectbox(
                        f"**{provider_name}**",
                        options=options,
                        index=0,
                        key=f"model_{provider_name}"
                    )

    # Load providers with selected models
    providers = create_providers(
        cartesia_key=api_keys["cartesia"],
        inworld_key=api_keys["inworld"],
        elevenlabs_key=api_keys["elevenlabs"],
        hume_key=api_keys["hume"],
        speechify_key=api_keys["speechify"],
        cartesia_model=selected_models.get("Cartesia"),
        inworld_model=selected_models.get("Inworld AI"),
        elevenlabs_model=selected_models.get("ElevenLabs"),
        hume_model=selected_models.get("Hume"),
        speechify_model=selected_models.get("Speechify"),
    )

    # Display active providers
    st.success(f"✅ Loaded {len(providers)} TTS provider(s): {', '.join(providers.keys())}")

    # Text input
    st.markdown("---")
    st.subheader("Enter Text to Synthesize")

    default_text = "Hello! This is a test of the text-to-speech system. How does this sound?"
    text_input = st.text_area(
        "Text:",
        value=default_text,
        height=100,
        placeholder="Enter the text you want to convert to speech...",
    )

    # Generate button
    if st.button("🎵 Generate Speech", type="primary", use_container_width=True):
        if not text_input.strip():
            st.warning("Please enter some text to synthesize.")
            return

        # Create unique request folder
        _, request_folder = create_request_folder(text_input)

        st.markdown("---")
        st.subheader("Generated Audio")
        st.info(f"Text: `{text_input}`")

        # Create columns for each provider
        cols = st.columns(len(providers))

        # Generate audio for each provider
        for idx, (provider_name, provider) in enumerate(providers.items()):
            with cols[idx]:
                st.markdown(f"**{provider_name}**")

                try:
                    # Show progress
                    with st.spinner(f"Generating..."):
                        audio_data = provider.synthesize(text_input)

                    # Detect audio format
                    audio_format = get_audio_format(audio_data)
                    if not audio_format:
                        # Default to mp3 if detection fails
                        audio_format = "mp3"

                    # Save permanently to data folder
                    saved_path = save_audio_permanent(
                        audio_data, provider_name, audio_format, request_folder
                    )

                    # Also save to temp file for immediate playback
                    temp_file = save_audio_temp(audio_data, audio_format)

                    # Display audio player
                    st.audio(temp_file, format=f"audio/{audio_format}")

                    # Show success message with path
                    st.success("✓ Generated")
                    st.caption(f"Saved: {saved_path.name}")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    # History section
    st.markdown("---")
    st.subheader("Recent History")

    history = get_generation_history(limit=5)

    if not history:
        st.info("No previous generations found. Generate some audio to see history!")
    else:
        for uuid, folder_path, timestamp, text in history:
            with st.expander(
                f"{text[:50]}{'...' if len(text) > 50 else ''} - {timestamp.strftime('%Y-%m-%d %H:%M:%S') if timestamp else 'Unknown'}"
            ):
                st.markdown(f"**Text:** {text}")

                # Find all audio files in the folder
                audio_files = list(folder_path.glob("*.mp3")) + list(folder_path.glob("*.wav"))

                if audio_files:
                    # Create columns for audio players
                    num_files = len(audio_files)
                    cols = st.columns(num_files)

                    for idx, audio_file in enumerate(sorted(audio_files)):
                        with cols[idx]:
                            # Extract provider name from filename
                            provider_name = audio_file.stem.replace("_", " ").title()
                            st.markdown(f"**{provider_name}**")

                            # Determine audio format
                            audio_format = audio_file.suffix[1:]  # Remove the dot
                            st.audio(str(audio_file), format=f"audio/{audio_format}")
                else:
                    st.warning("No audio files found for this generation.")

    # Instructions
    st.markdown("---")
    with st.expander("ℹ️ Instructions"):
        st.markdown(
            """
            ### How to Use

            1. **Enter your text** in the text area above
            2. Click the **Generate Speech** button
            3. Listen to the audio generated by each TTS provider
            4. Compare the quality, naturalness, and expressiveness

            ### Data Storage

            All generated audio files are automatically saved to the `data/` folder:
            - Each request gets a unique UUID
            - A subfolder is created: `data/<uuid>/`
            - The request text is saved as `request.txt`
            - Audio files are saved with provider names: `cartesia.wav`, `elevenlabs.mp3`, etc.

            ### Providers

            - **Cartesia**: Uses Sonic-3 model with Katie voice
            - **Inworld AI**: Uses Ashley voice with inworld-tts-1 model
            - **ElevenLabs**: Uses Flash v2.5 model for fast generation
            - **Hume**: Uses Octave 2 for emotionally expressive speech
            - **Speechify**: Uses Simba English model

            ### Tips

            - Try different types of text: conversational, formal, technical
            - Test punctuation and emphasis
            - Compare speed, naturalness, and clarity
            - Listen for artifacts or unnatural pauses
            """
        )


if __name__ == "__main__":
    main()
