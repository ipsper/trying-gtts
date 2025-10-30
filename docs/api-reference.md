# API Reference

Complete reference for all API endpoints in the gTTS FastAPI application.

## Table of Contents
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Root Endpoint](#root-endpoint)
  - [Text-to-Speech](#text-to-speech)
  - [Languages](#languages)
  - [Health Check](#health-check)
- [Request/Response Formats](#requestresponse-formats)
- [Error Responses](#error-responses)
- [Rate Limiting](#rate-limiting)

## Base URL

```
http://localhost:8088
```

Replace `8088` with your configured port if different.

## Authentication

Currently, the API does not require authentication. For production use, consider adding API key authentication or OAuth2.

## Endpoints

### Root Endpoint

Get API information and available endpoints.

**Endpoint:** `GET /api/v1/`

**Response:**
```json
{
  "message": "Welcome to gTTS API!",
  "version": "1.0.0",
  "endpoints": {
    "POST /api/v1/tts": "Convert text to speech (returns MP3 file)",
    "GET /api/v1/languages": "List available languages"
  },
  "documentation": {
    "swagger": "/docs",
    "redoc": "/redoc"
  }
}
```

**Status Codes:**
- `200 OK` - Success

**Example:**
```bash
curl http://localhost:8088/api/v1/
```

---

### Text-to-Speech

Convert text to speech and receive an MP3 audio file.

**Endpoint:** `POST /api/v1/tts`

**Request Headers:**
- `Content-Type: application/json`

**Request Body:**
```json
{
  "text": "string",  // Required, 1-5000 characters
  "lang": "string"   // Optional, default: "en"
}
```

**Request Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | string | Yes | - | Text to convert (1-5000 chars) |
| `lang` | string | No | `"en"` | ISO 639-1 language code |

**Validation Rules:**
- Text cannot be empty or only whitespace
- Text must be 1-5000 characters
- Text must be JSON-safe (no invalid control characters)
- Language code must be valid

**Response:**
- **Content-Type:** `audio/mpeg`
- **Body:** MP3 audio file
- **Filename:** `speech_{lang}.mp3`

**Status Codes:**
- `200 OK` - Success, returns MP3 file
- `400 Bad Request` - Invalid language code or TTS generation failed
- `422 Unprocessable Entity` - Validation error (invalid text format)
- `500 Internal Server Error` - Server error

**Example Request:**
```bash
curl -X POST "http://localhost:8088/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world!", "lang":"en"}' \
  --output hello.mp3
```

**Example with Multi-line Text:**
```bash
curl -X POST "http://localhost:8088/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{"text":"Line 1.\nLine 2.\nLine 3.", "lang":"en"}' \
  --output multiline.mp3
```

---

### Languages

Get list of supported languages.

**Endpoint:** `GET /api/v1/languages`

**Response:**
```json
{
  "languages": {
    "sv": "Swedish",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "zh-CN": "Chinese (Simplified)",
    "ar": "Arabic",
    "hi": "Hindi",
    "ko": "Korean"
  }
}
```

**Status Codes:**
- `200 OK` - Success

**Example:**
```bash
curl http://localhost:8088/api/v1/languages
```

---

### Health Check

Check if the service is running and healthy.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "gTTS API",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

**Example:**
```bash
curl http://localhost:8088/health
```

## Request/Response Formats

### Content Types

**Request:**
- `application/json` - For JSON payloads

**Response:**
- `application/json` - For JSON responses
- `audio/mpeg` - For MP3 files (TTS endpoint)

### Character Encoding

All text must be UTF-8 encoded.

### Special Characters

- **Newlines:** Use `\n` escape sequence in JSON
- **Quotes:** Escape with `\"`
- **Backslash:** Escape with `\\`

**Example:**
```json
{
  "text": "He said, \"Hello!\"\nNext line.",
  "lang": "en"
}
```

## Error Responses

### Format

All error responses follow this format:

```json
{
  "detail": "Error message"
}
```

Or for validation errors:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "text"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

### Common Error Codes

#### 400 Bad Request

**Causes:**
- Invalid language code
- TTS generation failed

**Example Response:**
```json
{
  "detail": "Failed to generate speech: Invalid language code. Please check the language code."
}
```

#### 422 Unprocessable Entity

**Causes:**
- Text is empty
- Text too long (>5000 chars)
- Text contains only whitespace
- Invalid JSON format
- Missing required fields

**Example Response:**
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "text"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```

#### 500 Internal Server Error

**Causes:**
- Unexpected server error
- File system issues

**Example Response:**
```json
{
  "detail": "Internal server error: ..."
}
```

### Error Handling Examples

#### Python

```python
import requests

response = requests.post(url, json=payload)

if response.status_code == 200:
    # Success
    with open("output.mp3", "wb") as f:
        f.write(response.content)
elif response.status_code == 422:
    # Validation error
    errors = response.json()
    print("Validation errors:", errors['detail'])
elif response.status_code == 400:
    # Bad request
    error = response.json()
    print("Error:", error['detail'])
else:
    # Other error
    print(f"HTTP {response.status_code}")
```

## Rate Limiting

Currently, there is no rate limiting implemented. For production use, consider adding rate limiting middleware.

**Example with slowapi:**

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/tts")
@limiter.limit("10/minute")
async def text_to_speech(request: Request, tts_request: TextToSpeechRequest):
    # ... implementation
```

## Interactive Documentation

### Swagger UI

Access interactive API documentation at:

```
http://localhost:8088/docs
```

Features:
- Try out endpoints directly
- View request/response schemas
- See example requests
- Download responses

### ReDoc

Access alternative documentation at:

```
http://localhost:8088/redoc
```

Features:
- Clean, readable format
- Detailed schema documentation
- Code samples
- Searchable

## OpenAPI Specification

Download the OpenAPI spec at:

```
http://localhost:8088/openapi.json
```

Use this with tools like:
- Postman
- Insomnia
- OpenAPI Generator (for client SDKs)

## Language Codes Reference

### Common Language Codes (ISO 639-1)

| Code | Language |
|------|----------|
| `sv` | Swedish |
| `en` | English |
| `es` | Spanish |
| `fr` | French |
| `de` | German |
| `it` | Italian |
| `pt` | Portuguese |
| `ru` | Russian |
| `ja` | Japanese |
| `zh-CN` | Chinese (Simplified) |
| `ar` | Arabic |
| `hi` | Hindi |
| `ko` | Korean |
| `da` | Danish |
| `nl` | Dutch |
| `fi` | Finnish |
| `no` | Norwegian |
| `pl` | Polish |
| `tr` | Turkish |

### Common Mistakes

- ❌ `se` → ✅ `sv` (Swedish)
- ❌ `dk` → ✅ `da` (Danish)
- ❌ `cz` → ✅ `cs` (Czech)

## Limitations

### Text Length
- Minimum: 1 character
- Maximum: 5000 characters

### Supported Audio Format
- Only MP3 format is supported
- Sample rate and quality are determined by gTTS library

### Language Support
- Depends on Google TTS support
- Not all languages may have the same quality
- Some language codes may not be supported

## Next Steps

- See [examples.md](examples.md) for usage examples
- See [troubleshooting.md](troubleshooting.md) for common issues
- See [configuration.md](configuration.md) for setup options

