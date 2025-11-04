# Interactive output.

Develop a streamlit application that can be used to assess the quality of text-to-speech systems. The application should allow a user to enter in free text and use a variety of services to generate speech. The results should be displayed in a so that a user can listen and compare. 

We will compare the following TTS services:
- Cartesia
- Inworld AI
- ElevenLabs
- Hume
- Speechify


Create a modular system that can add new providers easily. Use batch services instead of streaming.

## Technical Stack

- Python
- Streamlit

## Required Documentation
Use the web to investigate each of these applications. Do not use their SDK directly.

- Cartesia:
    - API Reference: https://docs.cartesia.ai/api-reference/tts/bytes
    - TTS Documentation: https://docs.cartesia.ai/build-with-cartesia/tts-models/latest
- Inworld
    - Documentation: https://docs.inworld.ai/docs/quickstart-tts
    - API Reference: https://docs.inworld.ai/api-reference/ttsAPI/texttospeech/synthesize-speech
- ElevenLabs 
    - API Reference: https://elevenlabs.io/docs/api-reference/text-to-speech/convert
    - TTS Documentation: https://elevenlabs.io/docs/capabilities/text-to-speech
- Hume
    - Using API key: https://dev.hume.ai/docs/introduction/api-key
    - TTS Documentation: https://dev.hume.ai/docs/text-to-speech-tts/overview
    - API Reference: https://dev.hume.ai/reference/text-to-speech-tts/synthesize-json
- Speechify
    - TTS Documentation: https://docs.sws.speechify.com/docs/get-started/quickstart
    - API Reference: https://docs.sws.speechify.com/api-reference/api-reference/tts/audio/speech


environment variables can be found in .env