#!/bin/bash

# Text-to-Speech Playback Script
# Generate and play audio from text using the gTTS API
# 
# Usage: ./scripts/speak.sh "Your text here" [language_code]
# Example: ./scripts/speak.sh "Hello world" en

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PORT="${GTTS_PORT:-8088}"
API_URL="http://localhost:${PORT}/api/v1/tts"

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to show help
show_help() {
    echo "Usage: $0 \"text to speak\" [language_code]"
    echo ""
    echo "Generate speech from text and play it immediately"
    echo ""
    echo "Arguments:"
    echo "  text           Text to convert to speech (required)"
    echo "  language_code  Language code (default: 'en')"
    echo ""
    echo "Examples:"
    echo "  $0 \"Hello world\""
    echo "  $0 \"Hej världen\" sv"
    echo "  $0 \"Bonjour le monde\" fr"
    echo "  $0 \"Hola mundo\" es"
    echo "  $0 \"Guten Tag\" de"
    echo ""
    echo "Common language codes:"
    echo "  en - English"
    echo "  sv - Swedish"
    echo "  es - Spanish"
    echo "  fr - French"
    echo "  de - German"
    echo "  it - Italian"
    echo "  ja - Japanese"
    echo "  zh - Chinese"
}

# Check if help is requested
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    show_help
    exit 0
fi

# Check if text is provided
if [ -z "$1" ]; then
    print_error "No text provided"
    echo ""
    show_help
    exit 1
fi

TEXT="$1"
LANG="${2:-en}"

print_info "Generating speech..."
print_info "Text: ${TEXT}"
print_info "Language: ${LANG}"

# Create temporary file for audio
TEMP_FILE=$(mktemp /tmp/gtts_audio_XXXXXX.mp3)

# Make API request and save to temp file
HTTP_CODE=$(curl -s -w "%{http_code}" -X POST "${API_URL}" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"${TEXT}\", \"lang\": \"${LANG}\"}" \
    -o "${TEMP_FILE}")

if [ "${HTTP_CODE}" != "200" ]; then
    print_error "API request failed with HTTP ${HTTP_CODE}"
    if [ -f "${TEMP_FILE}" ]; then
        cat "${TEMP_FILE}"
        rm "${TEMP_FILE}"
    fi
    exit 1
fi

# Check if file was created and has content
if [ ! -s "${TEMP_FILE}" ]; then
    print_error "No audio data received"
    rm "${TEMP_FILE}"
    exit 1
fi

print_info "Audio generated successfully ($(du -h "${TEMP_FILE}" | cut -f1))"

# Detect OS and play audio
if command -v afplay &> /dev/null; then
    # macOS
    print_info "Playing audio (macOS)..."
    afplay "${TEMP_FILE}"
elif command -v mpg123 &> /dev/null; then
    # Linux with mpg123
    print_info "Playing audio (mpg123)..."
    mpg123 -q "${TEMP_FILE}"
elif command -v ffplay &> /dev/null; then
    # ffplay (cross-platform)
    print_info "Playing audio (ffplay)..."
    ffplay -nodisp -autoexit -loglevel quiet "${TEMP_FILE}"
elif command -v vlc &> /dev/null; then
    # VLC
    print_info "Playing audio (VLC)..."
    vlc --play-and-exit --intf dummy "${TEMP_FILE}" 2>/dev/null
else
    print_warning "No audio player found!"
    print_info "Audio saved to: ${TEMP_FILE}"
    print_info "You can play it manually or install one of these players:"
    echo "  - macOS: afplay (built-in)"
    echo "  - Linux: mpg123 (apt-get install mpg123)"
    echo "  - Any OS: ffmpeg (with ffplay)"
    exit 0
fi

# Clean up
rm "${TEMP_FILE}"
print_info "Done!"

