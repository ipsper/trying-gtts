#!/bin/bash

# Play all audio files from audio_output directory
# Works on macOS and Linux

AUDIO_DIR="./audio_output"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔊 Playing audio files from $AUDIO_DIR"
echo

# Check if directory exists and has files
if [ ! -d "$AUDIO_DIR" ]; then
    echo "❌ Error: $AUDIO_DIR directory not found"
    echo "   Run tests with playback marker first:"
    echo "   ./run_tests.sh && pytest -m playback"
    exit 1
fi

# Count MP3 files
mp3_count=$(find "$AUDIO_DIR" -name "*.mp3" 2>/dev/null | wc -l)
if [ "$mp3_count" -eq 0 ]; then
    echo "❌ No MP3 files found in $AUDIO_DIR"
    echo "   Run tests with playback marker:"
    echo "   pytest -m playback"
    exit 1
fi

echo "Found $mp3_count audio files"
echo

# Detect OS and audio player
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    PLAYER="afplay"
    if ! command -v $PLAYER &> /dev/null; then
        echo "❌ Error: afplay not found (should be available on macOS)"
        exit 1
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux - try multiple players
    if command -v mpg123 &> /dev/null; then
        PLAYER="mpg123"
    elif command -v ffplay &> /dev/null; then
        PLAYER="ffplay -nodisp -autoexit"
    elif command -v vlc &> /dev/null; then
        PLAYER="vlc --play-and-exit --intf dummy"
    else
        echo "❌ Error: No audio player found"
        echo "   Install one of: mpg123, ffmpeg (ffplay), vlc"
        exit 1
    fi
else
    echo "❌ Error: Unsupported operating system: $OSTYPE"
    exit 1
fi

echo "Using player: $PLAYER"
echo

# Play each file in order
for audio_file in "$AUDIO_DIR"/*.mp3; do
    if [ -f "$audio_file" ]; then
        filename=$(basename "$audio_file")
        echo "▶️  Playing: $filename"
        $PLAYER "$audio_file"
        echo "   ✓ Done"
        echo
        # Small delay between files
        sleep 0.5
    fi
done

echo "✅ All audio files played!"
echo
echo "To run specific playback tests:"
echo "  pytest -m playback -k 'swedish'"
echo "  pytest tests/test_playback.py::test_english_greeting_playback"

