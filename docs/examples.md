# gTTS API Examples

This document provides examples of how to use the gTTS API with various programming languages and tools.

## Table of Contents
- [cURL Examples](#curl-examples)
- [Python Examples](#python-examples)
- [JavaScript Examples](#javascript-examples)
- [Error Handling](#error-handling)

## cURL Examples

### Basic Text-to-Speech

```bash
# English
curl -X POST "http://localhost:8088/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world!", "lang":"en"}' \
  --output hello.mp3

# Swedish (note: use 'sv' not 'se')
curl -X POST "http://localhost:8088/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hej världen!", "lang":"sv"}' \
  --output hej.mp3
```

### Multi-line Text

When you need newlines in your text, use `\n` escape sequences:

```bash
# Multi-line English text
curl -X POST "http://localhost:8088/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{"text":"Line one.\nLine two.\nLine three.", "lang":"en"}' \
  --output multiline.mp3

# Longer Swedish example
curl -X POST "http://localhost:8088/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{"text":"Planera, designa och genomföra manuella tester utifrån krav och användarflöden.\nBygga, underhålla och vidareutveckla automatiserade testsviter API- UI- och regressionstester.\nBidra till teststrategi och testmetodik i teamet.\nSamarbeta med verksamhet för att förstå affärslogik, riskflöden och regulatoriska krav.\nRapportera testresultat fel och förbättringsförslag.\nStötta teamet i att etablera shift-left testing och kvalitetsmedveten utveckling", "lang":"sv"}' \
  --output job_description.mp3
```

**Common Mistakes:**
- ❌ Using actual newlines in JSON: `"text":"Line 1\n<ENTER>Line 2"` - This breaks JSON!
- ❌ Using `"lang":"se"` for Swedish - Use `"sv"` instead
- ✅ Using `\n` for newlines: `"text":"Line 1.\nLine 2."`
- ✅ Using correct language code: `"lang":"sv"`

### Get Available Languages

```bash
curl http://localhost:8088/api/v1/languages
```

### Health Check

```bash
curl http://localhost:8088/health
```

## Python Examples

### Setup (recommended)

First, create a virtual environment to keep your system clean:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate  # On Windows

# Install requests library
pip install requests
```

### Using requests library

```python
import requests

# Generate speech
url = "http://localhost:8088/api/v1/tts"
payload = {
    "text": "Hello! This is a test of the text-to-speech API.",
    "lang": "en"
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    with open("output.mp3", "wb") as f:
        f.write(response.content)
    print("Audio file saved as output.mp3")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### Multi-line text in Python

```python
import requests

# Multi-line text works naturally in Python
text = """Planera, designa och genomföra manuella tester.
Bygga, underhålla och vidareutveckla automatiserade testsviter.
Bidra till teststrategi och testmetodik i teamet.
Samarbeta med verksamhet för att förstå affärslogik.
Rapportera testresultat fel och förbättringsförslag."""

url = "http://localhost:8088/api/v1/tts"
payload = {
    "text": text,  # Python handles the newlines correctly
    "lang": "sv"   # Swedish (not "se")
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    with open("job_description.mp3", "wb") as f:
        f.write(response.content)
    print("✓ Audio saved")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### With error handling

```python
import requests
from typing import Optional

def text_to_speech(text: str, lang: str = "en", output_file: str = "output.mp3") -> Optional[str]:
    """
    Convert text to speech using the gTTS API
    
    Args:
        text: Text to convert (1-5000 characters)
        lang: Language code (default: "en")
        output_file: Output filename (default: "output.mp3")
    
    Returns:
        Output filename if successful, None if failed
    """
    url = "http://localhost:8088/api/v1/tts"
    
    # Validate input
    if not text or len(text.strip()) == 0:
        print("Error: Text cannot be empty")
        return None
    
    if len(text) > 5000:
        print("Error: Text too long (max 5000 characters)")
        return None
    
    payload = {"text": text.strip(), "lang": lang}
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        with open(output_file, "wb") as f:
            f.write(response.content)
        
        print(f"✓ Audio saved as {output_file}")
        return output_file
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 422:
            print(f"Validation error: {response.json()}")
        elif response.status_code == 400:
            print(f"Bad request: {response.json()}")
        else:
            print(f"HTTP error: {e}")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Example usage
text_to_speech("Hello world!", "en", "hello.mp3")
text_to_speech("Bonjour le monde!", "fr", "bonjour.mp3")
```

## JavaScript Examples

### Using fetch API

```javascript
// Generate speech
async function textToSpeech(text, lang = 'en', outputFile = 'output.mp3') {
    try {
        const response = await fetch('http://localhost:8088/api/v1/tts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text, lang })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(`HTTP ${response.status}: ${JSON.stringify(error)}`);
        }

        const blob = await response.blob();
        
        // For browser: create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = outputFile;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        console.log(`✓ Audio saved as ${outputFile}`);
        return true;
        
    } catch (error) {
        console.error('Error:', error.message);
        return false;
    }
}

// Example usage
textToSpeech('Hello world!', 'en', 'hello.mp3');
```

### Node.js example

```javascript
const fs = require('fs');
const fetch = require('node-fetch');

async function textToSpeech(text, lang = 'en', outputFile = 'output.mp3') {
    try {
        const response = await fetch('http://localhost:8088/api/v1/tts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text, lang })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(`HTTP ${response.status}: ${JSON.stringify(error)}`);
        }

        const buffer = await response.buffer();
        fs.writeFileSync(outputFile, buffer);
        
        console.log(`✓ Audio saved as ${outputFile}`);
        return true;
        
    } catch (error) {
        console.error('Error:', error.message);
        return false;
    }
}

// Example usage
textToSpeech('Hello world!', 'en', 'hello.mp3');
```

## Error Handling

### Common Error Responses

#### 422 Validation Error
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

#### 400 Bad Request
```json
{
    "detail": "Failed to generate speech: Invalid language code. Please check the language code."
}
```

#### 500 Internal Server Error
```json
{
    "detail": "Internal server error: ..."
}
```

### Handling Invalid Input

```python
import requests

def safe_text_to_speech(text: str, lang: str = "en") -> bool:
    """Safely generate speech with comprehensive error handling"""
    
    # Client-side validation
    if not text or not text.strip():
        print("❌ Error: Text cannot be empty")
        return False
    
    if len(text) > 5000:
        print("❌ Error: Text too long (max 5000 characters)")
        return False
    
    url = "http://localhost:8088/api/v1/tts"
    payload = {"text": text.strip(), "lang": lang}
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            with open(f"speech_{lang}.mp3", "wb") as f:
                f.write(response.content)
            print(f"✓ Success: Audio saved")
            return True
            
        elif response.status_code == 422:
            errors = response.json()
            print(f"❌ Validation error:")
            for error in errors.get('detail', []):
                print(f"  - {error.get('msg', 'Unknown error')}")
            return False
            
        elif response.status_code == 400:
            detail = response.json().get('detail', 'Unknown error')
            print(f"❌ Bad request: {detail}")
            return False
            
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the server running?")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

# Examples
safe_text_to_speech("Hello world!", "en")
safe_text_to_speech("", "en")  # Will fail validation
safe_text_to_speech("Hello!", "invalid")  # Will fail with bad request
```

## Common Issues and Solutions

### Issue 1: JSON decode error with multi-line text

**Problem:** 
```bash
# This FAILS - actual newlines break JSON
curl -X POST "http://localhost:8088/api/v1/tts" \
  -d '{
  "text": "Line 1
Line 2",
  "lang": "sv"
}'
# Error: JSON decode error - Invalid control character
```

**Solution:**
```bash
# Use \n escape sequences for newlines
curl -X POST "http://localhost:8088/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{"text":"Line 1\nLine 2", "lang":"sv"}' \
  --output output.mp3
```

### Issue 2: Invalid language code

**Problem:**
```bash
# "se" is NOT a valid language code
curl -d '{"text":"Hej!", "lang":"se"}'
# Error: Failed to generate speech
```

**Solution:**
```bash
# Use "sv" for Swedish (ISO 639-1 code)
curl -d '{"text":"Hej!", "lang":"sv"}'
```

**Common language code mistakes:**
- ❌ `se` → ✅ `sv` (Swedish)
- ❌ `dk` → ✅ `da` (Danish)
- ❌ `no` → ✅ `nb` or `nn` (Norwegian)

### Issue 3: Text too long

**Problem:**
```bash
# Text over 5000 characters
curl -d '{"text":"very very long text...", "lang":"en"}'
# Error: String should have at most 5000 characters
```

**Solution:** Split into multiple requests or reduce text length.

## Best Practices

1. **Always validate input** before sending to the API
2. **Handle errors gracefully** with appropriate user feedback
3. **Use timeouts** to prevent hanging requests
4. **Trim whitespace** from text input
5. **Check text length** (1-5000 characters)
6. **Verify language codes** against the `/api/v1/languages` endpoint
7. **Use proper JSON encoding** for special characters (use `\n` for newlines)
8. **Use correct language codes** (e.g., `sv` not `se` for Swedish)

## Additional Resources

- API Documentation: http://localhost:8088/docs
- ReDoc Documentation: http://localhost:8088/redoc
- Health Check: http://localhost:8088/health

