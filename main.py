"""Main Streamlit application for TTS evaluation."""

import os
import json
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

from src.providers import create_providers
from src.utils.audio import (
    get_audio_format,
    create_request_folder,
    save_audio_permanent,
)
from src.utils.emotion import (
    parse_emotion_tags,
    SUPPORTED_EMOTIONS,
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
        List of tuples (uuid, folder_path, timestamp, text, provider_settings) sorted by newest first
    """
    data_dir = Path.cwd() / "data"
    if not data_dir.exists():
        return []

    generations = []
    for folder in data_dir.iterdir():
        if folder.is_dir():
            # Try new JSON format first
            request_json = folder / "request.json"
            request_txt = folder / "request.txt"

            if request_json.exists():
                try:
                    with open(request_json, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        timestamp = datetime.fromisoformat(data["timestamp"])
                        text = data["text"]
                        provider_settings = data.get("provider_settings", [])
                        generations.append(
                            (folder.name, folder, timestamp, text, provider_settings)
                        )
                except Exception:
                    continue
            elif request_txt.exists():
                # Support old format for backward compatibility
                try:
                    with open(request_txt, "r", encoding="utf-8") as f:
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
                        generations.append((folder.name, folder, timestamp, text, []))
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

    # Sidebar - Model Selection
    with st.sidebar:
        st.header("⚙️ Model Settings")
        st.markdown("Select the model for each TTS provider:")
        st.markdown("---")

        # Determine available providers
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

        # Store selected models
        selected_models = {}

        for provider_name in available_providers:
            options = MODEL_OPTIONS.get(provider_name, [])
            if options:
                selected_models[provider_name] = st.selectbox(
                    f"{provider_name}", options=options, index=0, key=f"model_{provider_name}"
                )
                st.markdown("")  # Add spacing

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

    st.title("🎙️ Text-to-Speech Evaluation Tool")
    st.markdown("Compare the quality of different text-to-speech services side-by-side.")

    # Display active providers
    st.success(f"✅ Loaded {len(providers)} TTS provider(s): {', '.join(providers.keys())}")
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
            """
        )

    # Initialize session state for text input
    if "text_input" not in st.session_state:
        st.session_state.text_input = (
            "Hello! This is a test of the text-to-speech system. How does this sound?"
        )

    # Text input
    st.markdown("---")

    text_input = st.text_area(
        "Text:",
        value=st.session_state.text_input,
        height=100,
        placeholder="Enter the text you want to convert to speech...",
        key="text_area_widget",
    )

    # Update session state when text changes
    st.session_state.text_input = text_input

    # Emotion buttons
    st.markdown("**Add Emotion Tags**")
    st.text(
        "You can add emotions like <tag>EMOTION</tag>. Supported emotions are laughter, angry, excited, sad and scared. Not every model supports emotions. Unsupported emotions will be stripped out"
    )

    # Show which models support emotions
    st.markdown("---")
    emotion_support_info = []
    for provider_name, provider in providers.items():
        if provider.can_emote:
            emotion_support_info.append(f"✅ {provider_name}")
        else:
            emotion_support_info.append(f"❌ {provider_name}")

    with st.expander("🎭 Emotion Support by Provider"):
        st.markdown(" | ".join(emotion_support_info))
        st.caption("✅ = Supports emotions | ❌ = Does not support emotions (tags will be removed)")

    # Initialize session state for generation tracking
    if "last_generation" not in st.session_state:
        st.session_state.last_generation = None

    # Generate button
    if st.button("🎵 Generate Speech", type="primary", use_container_width=True):
        if not text_input.strip():
            st.warning("Please enter some text to synthesize.")
            return
        # Collect provider settings
        provider_settings_list = [provider.settings for provider in providers.values()]

        # Create unique request folder
        request_uuid, request_folder = create_request_folder(text_input, provider_settings_list)

        # Dictionary to store audio file paths
        audio_files = {}

        # Generate audio for each provider
        for provider_name, provider in providers.items():
            try:
                # Show progress
                with st.spinner(f"Generating {provider_name}..."):
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

                # Store the saved path
                audio_files[provider_name] = {
                    "path": str(saved_path),
                    "format": audio_format,
                }

            except Exception as e:
                audio_files[provider_name] = {"error": str(e)}

        # Store generation info in session state
        st.session_state.last_generation = {
            "uuid": request_uuid,
            "folder": request_folder,
            "text": text_input,
            "providers": list(providers.keys()),
            "audio_files": audio_files,
        }

    # Display generated audio if available
    if st.session_state.last_generation is not None:
        gen_info = st.session_state.last_generation

        st.markdown("---")
        st.subheader("Generated Audio")
        st.markdown(f"**Request Text:** {gen_info['text']}")
        st.info(f"📁 Request UUID: `{gen_info['uuid']}`")

        # Create columns for each provider
        cols = st.columns(len(gen_info["providers"]))

        # Display audio for each provider
        for idx, provider_name in enumerate(gen_info["providers"]):
            with cols[idx]:
                st.markdown(f"**{provider_name}**")

                audio_info = gen_info["audio_files"].get(provider_name, {})

                if "error" in audio_info:
                    st.error(f"❌ Error: {audio_info['error']}")
                elif "path" in audio_info:
                    # Display audio player
                    audio_path = audio_info["path"]
                    audio_format = audio_info["format"]
                    st.audio(audio_path, format=f"audio/{audio_format}")

                    # Show success message
                    st.success("✓ Generated")
                    st.caption(f"Saved: {Path(audio_path).name}")

    # Display preference selection if there's a generation
    if st.session_state.last_generation is not None:
        gen_info = st.session_state.last_generation

        st.markdown("---")
        st.subheader("📊 Select Your Preference")
        st.markdown("Which provider generated the best audio?")

        # Radio button for preference selection
        preference = st.radio(
            "Choose the provider with the best output:",
            options=gen_info["providers"],
            index=None,
            key="preference_radio",
            horizontal=True,
        )

        # Save button
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("💾 Save Preference", type="primary", disabled=(preference is None)):
                if preference:
                    # Save preference to result.json in the request folder
                    result_data = {
                        "text": gen_info["text"],
                        "preference": preference,
                    }

                    result_file = gen_info["folder"] / "result.json"
                    with open(result_file, "w", encoding="utf-8") as f:
                        json.dump(result_data, f, indent=2, ensure_ascii=False)

                    st.success(f"✅ Preference saved: {preference}")

    # # History section
    # st.markdown("---")
    # st.subheader("📜 Recent Generations")

    # history = get_generation_history(limit=5)

    # if not history:
    #     st.info("No previous generations found. Generate some audio to see history!")
    # else:
    #     for uuid, folder_path, timestamp, text, provider_settings in history:
    #         with st.expander(
    #             f"🎵 {text[:50]}{'...' if len(text) > 50 else ''} - {timestamp.strftime('%Y-%m-%d %H:%M:%S') if timestamp else 'Unknown'}"
    #         ):
    #             st.caption(f"**UUID:** `{uuid}`")
    #             st.markdown(f"**Text:** {text}")

    #             # Display provider settings if available
    #             if provider_settings:
    #                 st.markdown("**Provider Settings:**")
    #                 for settings in provider_settings:
    #                     with st.expander(f"📋 {settings.get('name', 'Unknown Provider')}"):
    #                         st.json(settings)

    #             st.markdown("---")

    #             # Find all audio files in the folder
    #             audio_files = list(folder_path.glob("*.mp3")) + list(folder_path.glob("*.wav"))

    #             if audio_files:
    #                 # Create columns for audio players
    #                 num_files = len(audio_files)
    #                 cols = st.columns(num_files)

    #                 for idx, audio_file in enumerate(sorted(audio_files)):
    #                     with cols[idx]:
    #                         # Extract provider name from filename
    #                         provider_name = audio_file.stem.replace("_", " ").title()
    #                         st.markdown(f"**{provider_name}**")

    #                         # Determine audio format
    #                         audio_format = audio_file.suffix[1:]  # Remove the dot
    #                         st.audio(str(audio_file), format=f"audio/{audio_format}")
    #             else:
    #                 st.warning("No audio files found for this generation.")


if __name__ == "__main__":
    main()
