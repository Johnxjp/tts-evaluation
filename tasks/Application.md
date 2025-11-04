# Interactive output.

Develop a streamlit application that can be used to assess the quality of text-to-speech systems. The application should allow a user to enter in free text and use a variety of services to generate speech. The results should be displayed in a so that a user can listen and compare. 

We will compare the following TTS services:
- Cartesia
- Inworld AI
- ElevenLabs
- Hume
- Speechify


Create a modular system that can add new providers easily. Use batch services instead of streaming.

## Emotion tags
Some models accept emotion tags. To process emotion tags, we will ask the user to click a button to add them. This will
add xml-like tag to the text that each class will parse separately. The XML like tags are 
'<tag>anger</tag>'. For example, input text could be '<tag>anger</tag> I hate this job!'

We will also display to the user which models support tags. A boolean attribute 'can_emote' should be initialised in each class based on the model. If this is true, then the emotion tag will be converted into the right format for the model. If false, the emotion tag will be stripped out. 

### Streamlit
Emotions will be displayed as buttons beneath the text box. The following emotions are supported:
- laughter
- angry
- excited
- sad
- scared

The buttons should be aligned horizontally.

If a model can not emote, notify the user. 

### Providers

#### Speechify
Supported models: 'inworld-tts-1' and 'inworld-tts-1-max'

Speechify uses a special markup called SSML with format <speechify:style emotion="angry">. The mapping for emotions from button text to API is
- angry: angry
- excited: energetic
- sad: sad
- scared: terrified

laughter is not supported

#### Hume
Supported models: Octave '1'

Emotion should be added to 'description' key in utterance like this
```
    "utterances": [
      {
        "text": "Let us begin by taking a deep breath in.",
        "description": "calm, pedagogical", # style
        "voice": {
          "name": "Ava Song",
          "provider": "HUME_AI"
        }
      },
    ]
```

However Octave '2' does not support 'description' and should be removed if selected.

Hume uses comma-separated string in 'description' to mark emotion tags e.g. 'calm, angry'. The mapping from button text to API is
- laughter: laughter
- angry: angry
- excited: happy
- sad: sad
- scared: fearful


#### Inworld AI
Supported models: 'inworld-tts-1' and 'inworld-tts-1-max'

Inworld AI uses square brackets to mark emotion tags e.g. [angry]. The mapping from button text to API is
- laughter: laughing
- angry: angry
- excited: happy
- sad: sad
- scared: fearful


#### Eleven Labs
Supported models: 'eleven_v3'

Eleven Labs uses square brackets to mark emotion tags e.g. [angry]. The mapping from button text to API is
- laughter: laughter
- angry: angry
- excited: excited
- sad: sad
- scared: scared


#### Cartesia
Supported models: 'sonic-3' class models

Cartesia uses square brackets to mark emotion tags e.g. [angry]. The mapping from button text to API is
- laughter: laughter
- angry: angry
- excited: excited
- sad: sad
- scared: scared


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