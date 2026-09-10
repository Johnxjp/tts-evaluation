# TTS Evaluation

A side-by-side comparison of five commercial text-to-speech (TTS) APIs: **Cartesia**, **ElevenLabs**, **Hume**, **Inworld AI** and **Speechify**.

The repo contains a small Streamlit app that sends the same passage to every provider, stores the audio, and lets you listen and pick a favourite. Using that app, fifteen real-world passages covering six emotional registers were evaluated by hand against a fixed rubric. Cartesia, ElevenLabs, Hume and Inworld were scored on all fifteen. Speechify was scored on fourteen, because its clip for the property listing was never generated. Fourteen of the fifteen passages, with their audio, are included in this repo.

- Scoring data: [TTS Model Evaluation](https://docs.google.com/spreadsheets/d/1bXOn7FAQ6JIcFb9tLGuAeRoAWK9B4NC6tptKO4Lr0tw/edit?gid=0#gid=0) (Google Sheet)
- Audio for the fourteen public passages is checked in under `sample/` and browsable on the app's Audio samples page

## Headline results

| Provider | Model | Mean score (/12) | Accuracy (/5) | Prosody (/3) | Emotion (/2) | Other (/2) | Preferred |
|---|---|---:|---:|---:|---:|---:|---:|
| ElevenLabs | eleven_v3 | 10.7 | 4.9 | 2.6 | 1.5 | 1.8 | 5 |
| Speechify | simba-english | 10.7 | 4.5 | 2.5 | 1.7 | 2.0 | 3 |
| Cartesia | sonic-3 | 10.5 | 4.4 | 2.7 | 1.5 | 1.9 | 3 |
| Hume | Octave 1 | 10.5 | 4.2 | 2.7 | 1.7 | 1.8 | 4 |
| Inworld AI | inworld-tts-1 | 9.3 | 3.9 | 2.2 | 1.2 | 2.0 | 0 |

"Preferred" is the number of passages (out of 15) where that provider's clip was picked as the single best.

- **ElevenLabs v3** was the most accurate reader and the most often preferred. It missed the emotion on the sad and scared passages and tied with Hume for the most audio artefacts (a random gasp, an accent that drifted Australian).
- **Hume Octave 1** had the best prosody and emotion scores and tied ElevenLabs for the most perfect 12/12 clips (four each), but hallucinated words more than any other provider.
- **Speechify simba-english** was the only provider to land both the scared and surprised passages, and scored 12/12 on both sad clips. Its recurring weakness was rhythm and cadence.
- **Cartesia sonic-3** read with good prosody but under-played excitement and fear, and mispronounced the most standard words.
- **Inworld tts-1** finished last on every dimension and was never preferred. Odd inflections and unconvincing emotion were the recurring complaints.

With fifteen samples and a single listener, differences of a few tenths of a point are within noise. The gap between Inworld and the other four is the only clear separation.

## Methodology

### Test set

Fifteen passages were transcribed from real recordings so that each has a human reference performance to compare against. They cover excited, sad, angry, scared and surprised speech plus neutral narration, and deliberately include names, numbers, acronyms, a phone number, a URL and technical vocabulary.

| Title | Emotion | Source |
|---|---|---|
| [Solskjaer Champions League goal](https://youtu.be/1yON3ySblWQ?si=V2D5sVTv8RvijRUq&t=1168) | Excited | Football commentary |
| [The shot on Elo](https://youtu.be/9AOE9Gpv6Ho?si=A3NsQIWJ2Jev4YwD&t=3) | Excited | NBA commentary |
| [Aguerooo](https://youtu.be/U1fhiP2fjYc?si=Ov-yEua3-dIQwzWN&t=128) | Excited | Football commentary |
| [FIFA e-World Cup](https://www.youtube.com/shorts/-j5OyGmyBTU) | Excited | Esports penalty shoot-out commentary |
| [Jimmy Fallon on Kobe Bryant's death](https://youtu.be/aAByKcPJ5NQ?si=HvfGVLmNQ7JMGQLI&t=117) | Sad | Talk-show monologue |
| [George Alagiah's death](https://www.youtube.com/watch?v=tNv6iWJUnOg) | Sad | BBC News announcement |
| [Allen Iverson "practice"](https://youtu.be/eGDBR2L5kzI?si=IbN8Xhkc4cAlRid7&t=50) | Angry | Press conference |
| [Greta Thunberg "How dare you"](https://www.youtube.com/watch?v=xVlRompc1yE) | Angry | UN speech |
| [Emergency weather storm call](https://www.youtube.com/shorts/kvGvBroHlj4) | Scared | Tornado warning phone call |
| [Jimmy Fallon on the Kimmel suspension](https://youtu.be/_Gma4TPZCXg?si=fDmGC-O782mBBWy3&t=37) | Surprised | Talk-show monologue |
| [Met Office weather report](https://youtu.be/mTXMkoze-kE?si=1RgfARwysxw8k4KJ&t=80) | Neutral | Forecast with numbers |
| [Continence advert](https://youtu.be/J6VYDaO6k-I?si=kpoBEaa27VHKIbmP&t=19) | Neutral | Public-service ad with a phone number and URL |
| [Wikipedia: Benzyl benzoate](https://en.wikipedia.org/wiki/Benzyl_benzoate) | Neutral | Technical vocabulary |
| [Ed Sheeran Heinz ad](https://www.youtube.com/watch?v=keOaQm6RpBg) | Neutral | Long-form anecdote, around 200 words |
| Commercial property listing | Neutral | Addresses, measurements, an email and a phone number. Not included in the repo |

The reference clips are listed in `sample/samples.csv` and embedded on the Audio samples page next to each provider's audio.

### Generation

- Every provider received the identical text through its batch (non-streaming) HTTP endpoint, using one fixed voice per provider and default settings. There were no re-rolls: the first generation was the one scored.
- Emotional passages carried a single emotion tag where the emotion starts, written as `<tag>excited</tag>`. Neutral passages had no tag.
- Each provider adapter translates the tag into that API's own markup, or strips it if the selected model has no emotion control.

| Provider | Model | Voice | Emotion markup | Notes |
|---|---|---|---|---|
| Cartesia | sonic-3 | Kyle | Inline `[laughter]` or `<emotion value="..."/>` | sonic-3 models only |
| ElevenLabs | eleven_v3 | Mark | Audio tag `[excited]` | eleven_v3 only |
| Inworld AI | inworld-tts-1 | Alex | Audio tag `[happy]` | excited maps to happy, scared to fearful, laughter to laughing |
| Hume | Octave 1 | Two stock voices¹ | Emotion words in the utterance `description` | Octave 1 only; Octave 2 ignores descriptions |
| Speechify | simba-english | Oliver | SSML `<speechify:style emotion="...">` | excited maps to energetic, scared to terrified; laughter unsupported |

¹ The Hume voice was switched after the first four passages. See the caveats below. The voice used for each sample is recorded in its `request.json`.

### Scoring rubric

Each clip was checked against twelve yes/no questions in four categories. A category starts at full marks and loses one point per issue found, giving a total out of 12.

| Category | Points | Issues checked | Criteria |
|---|---:|---|---|
| Accuracy | 5 | Words missed, words hallucinated, standard word mispronounced, number mispronounced, acronym mispronounced, name mispronounced | Any words missed?<br>Any words hallucinated?<br>Any standard words mispronounced?<br>Any numbers mispronounced?<br>Any acronym mispronounced?<br>Any name mispronounced? |
| Prosody | 3 | Unnatural pauses, unnatural rhythm or cadence, odd inflections | Any unnatural pauses?<br>Any unnatural rhythm or cadence?<br>Any odd inflections? |
| Emotion | 2 | Emotion wrong or missing, emotion unconvincing | Was the emotion wrong or missing?<br>Was the emotion unconvincing? |
| Other | 2 | Glitches or artefacts in the audio | Were there any glitches or artifacts in the audio? |

After scoring all five clips for a passage, one clip was marked as the personal preference. This is a separate signal from the score and captures overall listenability rather than the absence of faults.

## Detailed results

### By emotional register

Mean total score out of 12.

| Emotion | Samples | Cartesia | Inworld | ElevenLabs | Hume | Speechify |
|---|---:|---:|---:|---:|---:|---:|
| Excited | 4 | 9.25 | 9.25 | 11.50 | 9.75 | 10.25 |
| Sad | 2 | 11.50 | 8.00 | 10.00 | 11.50 | 11.50 |
| Angry | 2 | 11.50 | 10.50 | 11.50 | 11.00 | 10.00 |
| Scared | 1 | 10.00 | 10.00 | 9.00 | 10.00 | 11.00 |
| Surprised | 1 | 10.00 | 10.00 | 9.00 | 11.00 | 12.00 |
| Neutral | 5 | 10.80 | 9.00 | 10.80 | 10.40 | 10.75 |

Emotion sub-score alone (0 to 2), which isolates how well each provider acted the requested register:

| Emotion | Cartesia | Inworld | ElevenLabs | Hume | Speechify |
|---|---:|---:|---:|---:|---:|
| Excited | 0.75 | 1.25 | 2.00 | 1.75 | 1.50 |
| Sad | 2.00 | 0.00 | 0.00 | 1.50 | 2.00 |
| Angry | 2.00 | 2.00 | 2.00 | 2.00 | 1.00 |
| Scared | 0.00 | 0.00 | 0.00 | 0.00 | 2.00 |
| Surprised | 1.00 | 1.00 | 0.00 | 2.00 | 2.00 |
| Neutral | 2.00 | 1.60 | 2.00 | 2.00 | 2.00 |

Fear was the hardest register: four of five providers failed the tornado warning outright. Sadness split the field, with Inworld and ElevenLabs missing it entirely while Cartesia and Speechify were flawless. Only ElevenLabs was consistently convincing on excited sports commentary.

### Failure modes

Number of clips flagged with each issue, out of 15 per provider (14 for Speechify).

| Issue | Cartesia | Inworld | ElevenLabs | Hume | Speechify |
|---|---:|---:|---:|---:|---:|
| Words missed | 0 | 3 | 1 | 1 | 0 |
| Words hallucinated | 0 | 4 | 0 | 5 | 1 |
| Standard word mispronounced | 4 | 3 | 0 | 2 | 1 |
| Number mispronounced | 0 | 2 | 0 | 1 | 1 |
| Acronym mispronounced | 1 | 1 | 0 | 0 | 1 |
| Name mispronounced | 4 | 4 | 1 | 3 | 3 |
| Unnatural pauses | 1 | 1 | 3 | 2 | 1 |
| Unnatural rhythm or cadence | 3 | 4 | 2 | 1 | 5 |
| Odd inflections | 1 | 7 | 1 | 1 | 1 |
| Emotion wrong or missing | 3 | 5 | 4 | 1 | 2 |
| Emotion unconvincing | 5 | 7 | 4 | 3 | 2 |
| Glitches or artefacts | 1 | 0 | 3 | 3 | 0 |

Name pronunciation was the most common accuracy fault across the board. The two football commentary passages (Solskjaer and Sheringham, Balotelli and Agüero) each tripped up four of the five providers. ElevenLabs was the only provider that never mispronounced a standard word, and it and Cartesia were the only two that never hallucinated words.

### Listener notes

Free-text notes and comments recorded alongside the scores:

- **Solskjaer, ElevenLabs:** a random gasp in the audio.
- **Continence advert, Inworld:** sounded excited for no reason on a neutral read.
- **Tornado warning, ElevenLabs:** the accent turned Australian part-way through.
- **Tornado warning, Speechify:** added gasps that were not in the text.
- **Fallon on Kimmel, Cartesia:** audio not clear.
- **Iverson, Cartesia:** unnatural pacing. **Iverson, ElevenLabs:** a nice rise in frustration.
- **Greta Thunberg, ElevenLabs:** just a bit too slow.
- **Property listing, ElevenLabs:** impressive handling of the measurements in metres, with some high-pitched sound.

### Caveats

- One listener, one pass, not blind. The scores are a single person's judgement.
- Fifteen passages is small. The scared and surprised registers have one passage each, so those rows are single data points.
- One voice per provider, except Hume. A different voice choice could change the ranking.
- Hume's voice was switched part-way through the run. The first four passages generated (Solskjaer, the shot on Elo, Fallon on Kobe Bryant, Alagiah) use one stock Hume voice, and every later passage uses the Booming American Narrator voice that is now the default in the code. Two of Hume's four perfect scores and two of its four preference wins came from the first voice, so Hume's row blends two voices and is not directly comparable to the others.
- Speechify was not scored on the property listing because that generation was not produced, so its averages are over 14 clips.

## Running the app

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env    # add your API keys
uv run streamlit run main.py
```

Keys are read from these environment variables, and can also be pasted into the sidebar at runtime:

```
CARTESIA_API_KEY
INWORLD_API_KEY
ELEVENLABS_API_KEY
HUME_API_KEY
SPEECHIFY_API_KEY
```

Only providers with a key are loaded. The sidebar also lets you choose a model per provider.

**Generate page.** Enter text, optionally with emotion tags such as `<tag>angry</tag>` (supported emotions: laughter, angry, excited, sad, scared). Click Generate Speech to synthesise with every loaded provider. Each request gets a UUID folder under `data/` containing `request.json` (timestamp, text and the exact provider settings used) and one audio file per provider. After listening you can pick the best clip and save it to `result.json` in the same folder.

**Audio samples page.** Reads `sample/samples.csv` and, for each sample, shows the transcript, embeds the reference YouTube clip at the right timestamp, and plays each provider's audio. Scores are not shown here; they live in the Google Sheet.

## Project layout

```
main.py                  Streamlit app: Generate and Audio samples pages
src/providers/base.py    TTSProvider abstract base class
src/providers/*.py       One adapter per provider (cartesia, elevenlabs, hume, inworld, speechify)
src/utils/audio.py       Request folders, audio saving, format detection
sample/samples.csv       Metadata for the evaluated samples (title, emotion, ID, reference URL)
sample/<uuid>/           request.json plus one mp3 per provider for each evaluated sample
data/<uuid>/             Output of new generations (gitignored)
tasks/Application.md     Original build spec for the app
```

## Adding a provider

1. Create `src/providers/<name>.py` with a class that subclasses `TTSProvider` and implements `name`, `settings`, `can_emote` and `synthesize`. `synthesize` takes the raw text (possibly containing `<tag>emotion</tag>` markers), converts or strips the tags, calls the provider's batch endpoint with plain `requests`, and returns the audio bytes.
2. Register it in `create_providers` in `src/providers/__init__.py`.
3. Add its model options to `MODEL_OPTIONS` and an API key input in `main.py`.
