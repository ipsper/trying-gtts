# Text-to-Speech Playback Script

The `speak.sh` script provides a quick way to generate and play audio from text using the gTTS API.

## Features

- 🎵 Generate and play audio in one command
- 🌍 Support for multiple languages
- 🔊 Automatic audio player detection (macOS, Linux, Windows)
- 🧹 Automatic cleanup of temporary files
- ⚡ Fast and easy to use

## Installation

The script is located at `scripts/speak.sh` and requires:

1. The gTTS API running on `localhost:8088` (or custom port via `GTTS_PORT`)
2. An audio player installed on your system

### Supported Audio Players

The script automatically detects and uses available players:

- **macOS**: `afplay` (built-in, no installation needed)
- **Linux**: 
  - `mpg123`: `sudo apt-get install mpg123` or `sudo yum install mpg123`
  - `ffplay` (part of ffmpeg): `sudo apt-get install ffmpeg`
- **Cross-platform**: 
  - `vlc`: Available for all operating systems

## Usage

### Basic Syntax

```bash
./scripts/speak.sh "text to speak" [language_code]
```

### Examples

#### English (default)
```bash
./scripts/speak.sh "Hello world"
```

#### Swedish
```bash
./scripts/speak.sh "Hej världen" sv
```

#### Spanish
```bash
./scripts/speak.sh "Hola mundo" es
```

#### French
```bash
./scripts/speak.sh "Bonjour le monde" fr
```

#### German
```bash
./scripts/speak.sh "Guten Tag" de
```

#### Multi-line text
```bash
./scripts/speak.sh "This is line one.
This is line two.
And this is line three." en
```

### Common Language Codes

| Code | Language   |
|------|-----------|
| `en` | English   |
| `sv` | Swedish   |
| `es` | Spanish   |
| `fr` | French    |
| `de` | German    |
| `it` | Italian   |
| `pt` | Portuguese|
| `ja` | Japanese  |
| `zh` | Chinese   |
| `ar` | Arabic    |
| `ru` | Russian   |

See [API Reference](api-reference.md#supported-languages) for the complete list.

## Configuration

### Custom Port

If your API runs on a different port:

```bash
export GTTS_PORT=9000
./scripts/speak.sh "Hello" en
```

Or inline:

```bash
GTTS_PORT=9000 ./scripts/speak.sh "Hello" en
```

## How It Works

1. The script sends a POST request to `/api/v1/tts` with your text and language
2. Receives the MP3 audio file from the API
3. Saves it to a temporary file in `/tmp`
4. Detects your operating system and available audio players
5. Plays the audio using the best available player
6. Cleans up the temporary file automatically

## Troubleshooting

### No Audio Player Found

If you get a "No audio player found" message:

**macOS:**
- `afplay` is built-in, should work out of the box

**Linux:**
```bash
# Install mpg123 (recommended)
sudo apt-get install mpg123

# Or install ffmpeg
sudo apt-get install ffmpeg
```

**Windows (WSL):**
```bash
# Install mpg123
sudo apt-get install mpg123

# Note: You may need to configure audio output for WSL
```

### API Not Running

If you get "API request failed":

```bash
# Check if API is running
./scripts/manage.sh status

# Start API if needed
./scripts/manage.sh start
```

### Invalid Language Code

If you get an error about invalid language:

```bash
# Check available languages
curl http://localhost:8088/api/v1/languages

# Or visit the API docs
open http://localhost:8088/docs
```

### Audio File Issues

If the audio doesn't play but the file is saved:

```bash
# Play manually with your preferred player
afplay /tmp/saved_audio.mp3       # macOS
mpg123 /tmp/saved_audio.mp3       # Linux
vlc /tmp/saved_audio.mp3          # Any OS with VLC
```

## Advanced Usage

### Save Audio Without Playing

To save the audio file without playing:

```bash
curl -X POST 'http://localhost:8088/api/v1/tts' \
  -H 'Content-Type: application/json' \
  -d '{"text": "Your text here", "lang": "en"}' \
  -o output.mp3
```

### Batch Processing

Create multiple audio files:

```bash
#!/bin/bash
# save_speeches.sh

./scripts/speak.sh "Introduction" en
./scripts/speak.sh "Huvudsakligt innehåll" sv
./scripts/speak.sh "Conclusion" en
```

### Pipe Text from File

```bash
# Read text from file
TEXT=$(cat my_text.txt)
./scripts/speak.sh "$TEXT" en
```

### Integration with Other Tools

```bash
# Read from clipboard (macOS)
./scripts/speak.sh "$(pbpaste)" en

# Read from stdin
echo "Hello world" | xargs -I {} ./scripts/speak.sh "{}" en

# Speak command output
./scripts/speak.sh "$(date)" en
```

## Error Handling

The script provides clear error messages:

- **No text provided**: You must provide text as the first argument
- **API request failed**: Check if the API is running and accessible
- **No audio data received**: The API returned an empty response
- **No audio player found**: Install a supported audio player

All errors include helpful suggestions for resolution.

## Examples Gallery

### News Reader
```bash
./scripts/speak.sh "Breaking news: Scientists discover new method for text-to-speech synthesis" en
```

### Language Learning
```bash
./scripts/speak.sh "Guten Morgen, wie geht es Ihnen?" de
./scripts/speak.sh "Buenos días, cómo estás?" es
./scripts/speak.sh "Bonjour, comment allez-vous?" fr
```

### Accessibility
```bash
# Read documentation aloud
./scripts/speak.sh "$(cat README.md)" en

# Read error messages
ERROR_MSG=$(make test 2>&1 | tail -1)
./scripts/speak.sh "$ERROR_MSG" en
```

### Fun Examples
```bash
./scripts/speak.sh "I am not a robot. Or am I?" en
./scripts/speak.sh "To be or not to be, that is the question" en
./scripts/speak.sh "May the force be with you" en
```

## Related Documentation

- [API Reference](api-reference.md) - Full API documentation
- [Examples](examples.md) - More API usage examples
- [Configuration](configuration.md) - API configuration options
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

