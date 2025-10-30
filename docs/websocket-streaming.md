# WebSocket Streaming Guide

Real-time text-to-speech streaming using WebSocket connections for instant audio playback in browsers and applications.

## Overview

The WebSocket streaming endpoint (`/ws/tts`) provides a bi-directional communication channel that allows clients to send text and receive audio data in real-time. Unlike the REST API endpoint that returns a complete MP3 file, WebSocket streaming sends audio data in chunks as it's generated, enabling immediate playback.

## Features

- 🚀 **Real-time streaming** - Audio data sent in 8KB chunks
- 🔄 **Persistent connection** - Keep connection open for multiple requests
- 📊 **Status updates** - Receive progress notifications during generation
- 🎵 **Instant playback** - Start playing audio as soon as chunks arrive
- 🌐 **Browser-friendly** - Built-in web UI for easy testing
- ⚡ **Low latency** - Faster than REST API for interactive applications

## Quick Start

### Option 1: Web UI (Easiest)

Simply open in your browser:

```
http://localhost:8088/stream-player
```

1. Type or paste your text
2. Select language
3. Click "🎤 Speak"
4. Listen!

### Option 2: WebSocket Client

Connect to:

```
ws://localhost:8088/ws/tts
```

Or for HTTPS:

```
wss://your-domain.com/ws/tts
```

## WebSocket Protocol

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8088/ws/tts');

ws.onopen = () => {
    console.log('Connected to TTS WebSocket');
};
```

### Sending Requests

Send JSON with text and language:

```javascript
ws.send(JSON.stringify({
    text: "Hello, this is a test of WebSocket streaming",
    lang: "en"
}));
```

**Request Format:**
```json
{
    "text": "Your text here",
    "lang": "en"
}
```

**Fields:**
- `text` (string, required): Text to convert to speech (1-5000 characters)
- `lang` (string, optional): Language code (default: "en")

### Receiving Responses

The server sends three types of messages:

#### 1. Status Messages (JSON)

**Generating:**
```json
{
    "status": "generating",
    "message": "Generating speech for: Hello, this is a test..."
}
```

**Ready to stream:**
```json
{
    "status": "ready",
    "message": "Audio ready, streaming...",
    "size": 28672
}
```

**Complete:**
```json
{
    "status": "complete",
    "message": "Audio streaming complete"
}
```

**Error:**
```json
{
    "status": "error",
    "error": "Error message here"
}
```

#### 2. Audio Data (Binary)

After the "ready" message, audio chunks are sent as binary data (MP3 format).

```javascript
ws.onmessage = async (event) => {
    if (typeof event.data === 'string') {
        const message = JSON.parse(event.data);
        // Handle status messages
    } else {
        // Binary audio data
        const audioChunk = await event.data.arrayBuffer();
        // Collect chunks for playback
    }
};
```

## Complete JavaScript Example

```javascript
let ws = null;
let audioChunks = [];
let isReceiving = false;

function connect() {
    ws = new WebSocket('ws://localhost:8088/ws/tts');
    
    ws.onopen = () => {
        console.log('WebSocket connected');
    };
    
    ws.onmessage = async (event) => {
        if (typeof event.data === 'string') {
            const message = JSON.parse(event.data);
            
            switch(message.status) {
                case 'generating':
                    console.log('Generating:', message.message);
                    audioChunks = [];
                    isReceiving = false;
                    break;
                    
                case 'ready':
                    console.log('Ready to receive audio');
                    isReceiving = true;
                    break;
                    
                case 'complete':
                    console.log('Audio complete, playing...');
                    playAudio();
                    break;
                    
                case 'error':
                    console.error('Error:', message.error);
                    break;
            }
        } else {
            // Binary audio data
            if (isReceiving) {
                const chunk = await event.data.arrayBuffer();
                audioChunks.push(chunk);
            }
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
        console.log('WebSocket closed');
        ws = null;
    };
}

function playAudio() {
    // Combine all chunks into one blob
    const blob = new Blob(audioChunks, { type: 'audio/mpeg' });
    const url = URL.createObjectURL(blob);
    
    // Create and play audio
    const audio = new Audio(url);
    audio.play();
    
    audio.onended = () => {
        URL.revokeObjectURL(url);
        console.log('Playback complete');
    };
}

function speak(text, lang = 'en') {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        connect();
        setTimeout(() => speak(text, lang), 500);
        return;
    }
    
    ws.send(JSON.stringify({ text, lang }));
}

// Usage
connect();
setTimeout(() => {
    speak("Hello! This is a test of WebSocket streaming.", "en");
}, 1000);
```

## Python Example

```python
import asyncio
import websockets
import json

async def text_to_speech_stream(text, lang="en"):
    uri = "ws://localhost:8088/ws/tts"
    audio_chunks = []
    
    async with websockets.connect(uri) as websocket:
        # Send request
        await websocket.send(json.dumps({
            "text": text,
            "lang": lang
        }))
        
        # Receive responses
        async for message in websocket:
            if isinstance(message, str):
                # JSON status message
                data = json.loads(message)
                print(f"Status: {data['status']}")
                
                if data['status'] == 'error':
                    print(f"Error: {data['error']}")
                    break
                elif data['status'] == 'complete':
                    print("Audio complete!")
                    break
            else:
                # Binary audio data
                audio_chunks.append(message)
        
        # Save combined audio
        if audio_chunks:
            with open('output.mp3', 'wb') as f:
                for chunk in audio_chunks:
                    f.write(chunk)
            print(f"Saved {len(audio_chunks)} chunks to output.mp3")

# Run
asyncio.run(text_to_speech_stream(
    "Hello! This is a test of WebSocket streaming.",
    "en"
))
```

## Node.js Example

```javascript
const WebSocket = require('ws');
const fs = require('fs');

function textToSpeechStream(text, lang = 'en') {
    return new Promise((resolve, reject) => {
        const ws = new WebSocket('ws://localhost:8088/ws/tts');
        const audioChunks = [];
        
        ws.on('open', () => {
            console.log('Connected');
            ws.send(JSON.stringify({ text, lang }));
        });
        
        ws.on('message', (data) => {
            if (typeof data === 'string') {
                const message = JSON.parse(data);
                console.log(`Status: ${message.status}`);
                
                if (message.status === 'error') {
                    reject(new Error(message.error));
                    ws.close();
                } else if (message.status === 'complete') {
                    // Save audio
                    const buffer = Buffer.concat(audioChunks);
                    fs.writeFileSync('output.mp3', buffer);
                    console.log(`Saved ${audioChunks.length} chunks to output.mp3`);
                    resolve();
                    ws.close();
                }
            } else {
                // Binary audio data
                audioChunks.push(data);
            }
        });
        
        ws.on('error', reject);
    });
}

// Usage
textToSpeechStream(
    "Hello! This is a test of WebSocket streaming.",
    "en"
).then(() => {
    console.log('Done!');
}).catch((error) => {
    console.error('Error:', error);
});
```

## Advanced Usage

### Multiple Sequential Requests

You can send multiple requests on the same WebSocket connection:

```javascript
async function speakMultiple(texts, lang = 'en') {
    for (const text of texts) {
        await new Promise((resolve) => {
            let audioChunks = [];
            let isReceiving = false;
            
            const messageHandler = async (event) => {
                if (typeof event.data === 'string') {
                    const msg = JSON.parse(event.data);
                    
                    if (msg.status === 'ready') {
                        isReceiving = true;
                    } else if (msg.status === 'complete') {
                        playAudio(audioChunks);
                        ws.removeEventListener('message', messageHandler);
                        resolve();
                    }
                } else if (isReceiving) {
                    audioChunks.push(await event.data.arrayBuffer());
                }
            };
            
            ws.addEventListener('message', messageHandler);
            ws.send(JSON.stringify({ text, lang }));
        });
    }
}

// Usage
speakMultiple([
    "First message",
    "Second message",
    "Third message"
], "en");
```

### Auto-Reconnect

```javascript
class TTSWebSocket {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.reconnectInterval = 5000;
    }
    
    connect() {
        this.ws = new WebSocket(this.url);
        
        this.ws.onclose = () => {
            console.log('Disconnected, reconnecting...');
            setTimeout(() => this.connect(), this.reconnectInterval);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    speak(text, lang = 'en') {
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ text, lang }));
        } else {
            console.error('WebSocket not connected');
        }
    }
}

// Usage
const tts = new TTSWebSocket('ws://localhost:8088/ws/tts');
tts.connect();
```

## Web UI Features

The built-in web interface at `/stream-player` includes:

### Design Features
- 🎨 **Modern gradient UI** - Purple gradient background
- 📱 **Responsive design** - Works on all screen sizes
- ⌨️ **Large text area** - Easy text input
- 🌍 **Language selector** - 11 common languages
- 🎤 **Large speak button** - Clear call to action

### Functional Features
- ✅ **Auto-connect** - Connects on page load
- 🔄 **Auto-reconnect** - Reconnects if connection drops
- 📊 **Status indicators** - Shows generation progress
- 🎵 **Auto-play** - Plays audio immediately when ready
- ⚠️ **Error handling** - Clear error messages
- 🔒 **Disabled during generation** - Prevents multiple requests

### User Experience
- Loading spinner during generation
- Color-coded status messages (blue=info, green=success, red=error)
- Smooth animations and transitions
- Keyboard accessible
- No page refresh needed

## Comparison: WebSocket vs REST API

| Feature | WebSocket `/ws/tts` | REST `/api/v1/tts` |
|---------|-------------------|-------------------|
| Connection | Persistent | Per-request |
| Response Time | Real-time chunks | Complete file |
| Best For | Interactive apps | File downloads |
| Complexity | Higher | Lower |
| Browser Support | All modern | All browsers |
| Streaming | ✅ Yes | ❌ No |
| File Output | Manual save | Direct download |
| Multiple Requests | Same connection | New connection |

### When to Use WebSocket

✅ **Use WebSocket when:**
- Building interactive voice applications
- Need immediate audio feedback
- Want to reduce connection overhead for multiple requests
- Building chat-based applications
- Creating voice-enabled UIs

### When to Use REST API

✅ **Use REST API when:**
- Generating files for download
- Batch processing
- Simple one-off requests
- Need file metadata (filename, Content-Disposition)
- Integration with file-based workflows

## Troubleshooting

### WebSocket Connection Failed

**Problem:** Cannot connect to WebSocket

**Solutions:**
```bash
# Check if API is running
curl http://localhost:8088/health

# Check for firewall issues
./scripts/manage.sh status

# Try explicit port
ws://localhost:8088/ws/tts
```

### No Audio Playback

**Problem:** Audio doesn't play in browser

**Solutions:**
1. Check browser console for errors
2. Ensure user interaction (browsers require user gesture for audio)
3. Check audio chunks are being received
4. Verify MP3 format support

```javascript
// Debug: Check received data
ws.onmessage = async (event) => {
    console.log('Received:', event.data.constructor.name);
    if (event.data instanceof Blob) {
        console.log('Blob size:', event.data.size);
    }
};
```

### Connection Drops

**Problem:** WebSocket disconnects unexpectedly

**Solutions:**
```javascript
// Implement heartbeat
setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
        // Keep connection alive
        ws.send(JSON.stringify({ ping: true }));
    }
}, 30000);

// Add reconnect logic
ws.onclose = () => {
    console.log('Reconnecting...');
    setTimeout(connect, 1000);
};
```

### CORS Issues

**Problem:** CORS errors when connecting from different origin

**Solution:** Use same origin or configure CORS in FastAPI:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Performance Considerations

### Chunk Size

Current chunk size: **8192 bytes (8KB)**

- Smaller chunks: More real-time, more overhead
- Larger chunks: Less overhead, more latency

### Connection Limits

- WebSocket connections persist
- Monitor concurrent connections
- Set reasonable timeouts
- Implement connection pooling for high traffic

### Memory Usage

Audio chunks accumulate in memory:

```javascript
// Clear old chunks after playback
audio.onended = () => {
    audioChunks = [];
    URL.revokeObjectURL(url);
};
```

## Security Considerations

### Input Validation

- Text length limited to 5000 characters
- Language code validated server-side
- JSON parsing errors handled gracefully

### Rate Limiting

Consider implementing rate limiting for production:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

### Authentication

For production, add authentication:

```javascript
ws = new WebSocket('ws://localhost:8088/ws/tts', {
    headers: {
        'Authorization': 'Bearer ' + token
    }
});
```

## Best Practices

1. **Always handle errors**
   ```javascript
   ws.onerror = (error) => {
       console.error('WebSocket error:', error);
       // Show user-friendly message
   };
   ```

2. **Clean up resources**
   ```javascript
   window.onbeforeunload = () => {
       if (ws) ws.close();
   };
   ```

3. **Validate input before sending**
   ```javascript
   if (!text || text.length > 5000) {
       console.error('Invalid text length');
       return;
   }
   ```

4. **Implement timeouts**
   ```javascript
   const timeout = setTimeout(() => {
       console.error('Request timeout');
       ws.close();
   }, 30000);
   ```

5. **Use connection pooling for multiple requests**
   - Reuse the same WebSocket connection
   - Implement request queuing

## Related Documentation

- **[API Reference](api-reference.md)** - REST API endpoints
- **[Speech Playback Guide](speak.md)** - Command-line playback
- **[Examples](examples.md)** - More usage examples
- **[Troubleshooting](troubleshooting.md)** - Common issues

## Examples Repository

Find more examples at:
- JavaScript/Browser examples
- Python asyncio examples
- Node.js examples
- React integration examples
- Vue.js integration examples

## Support

For issues or questions:
1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Review error messages in browser console
3. Check API logs: `./scripts/manage.sh logs`
4. Test with the built-in web UI first

