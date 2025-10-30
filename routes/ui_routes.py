"""
UI routes for HTML pages
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["UI"])


@router.get("/audio-player", response_class=HTMLResponse)
async def audio_player():
    """
    Interactive web page for browsing and playing audio library
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Audio Library Player</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                padding: 40px;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 28px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 14px;
            }
            .stats {
                display: flex;
                gap: 20px;
                margin-bottom: 30px;
                padding: 20px;
                background: #f5f5f5;
                border-radius: 10px;
            }
            .stat {
                flex: 1;
                text-align: center;
            }
            .stat-value {
                font-size: 32px;
                font-weight: bold;
                color: #667eea;
            }
            .stat-label {
                color: #666;
                font-size: 14px;
                margin-top: 5px;
            }
            .audio-list {
                max-height: 500px;
                overflow-y: auto;
            }
            .audio-item {
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 15px;
                transition: all 0.3s;
            }
            .audio-item:hover {
                border-color: #667eea;
                background: #f9f9ff;
            }
            .audio-item.playing {
                border-color: #667eea;
                background: #e8f0fe;
            }
            .play-btn {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                border: none;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                font-size: 20px;
                cursor: pointer;
                flex-shrink: 0;
                transition: transform 0.2s;
            }
            .play-btn:hover {
                transform: scale(1.1);
            }
            .audio-info {
                flex: 1;
            }
            .audio-name {
                font-weight: 600;
                color: #333;
                margin-bottom: 5px;
                word-break: break-all;
            }
            .audio-meta {
                font-size: 12px;
                color: #666;
            }
            .audio-controls {
                display: flex;
                gap: 10px;
            }
            .icon-btn {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
                cursor: pointer;
                font-size: 16px;
                transition: all 0.2s;
            }
            .icon-btn:hover {
                background: #f5f5f5;
                border-color: #667eea;
            }
            .delete-btn:hover {
                background: #ffebee;
                border-color: #c62828;
                color: #c62828;
            }
            .no-files {
                text-align: center;
                padding: 60px 20px;
                color: #999;
            }
            .no-files-icon {
                font-size: 64px;
                margin-bottom: 20px;
            }
            .refresh-btn {
                padding: 12px 24px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                margin-bottom: 20px;
                transition: transform 0.2s;
            }
            .refresh-btn:hover {
                transform: translateY(-2px);
            }
            audio {
                width: 100%;
                margin-top: 20px;
                display: none;
            }
            audio.active {
                display: block;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎵 Audio Library</h1>
            <p class="subtitle">Browse and play saved audio files</p>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-value" id="totalFiles">0</div>
                    <div class="stat-label">Total Files</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="totalSize">0 MB</div>
                    <div class="stat-label">Total Size</div>
                </div>
            </div>
            
            <button class="refresh-btn" onclick="loadLibrary()">🔄 Refresh Library</button>
            
            <div class="audio-list" id="audioList"></div>
            
            <audio id="audioPlayer" controls></audio>
        </div>

        <script>
            let currentPlaying = null;
            const audioPlayer = document.getElementById('audioPlayer');
            
            async function loadLibrary() {
                try {
                    const response = await fetch('/api/v1/library');
                    const data = await response.json();
                    
                    document.getElementById('totalFiles').textContent = data.total_files;
                    
                    const totalSizeMB = data.files.reduce((sum, file) => sum + file.size_mb, 0);
                    document.getElementById('totalSize').textContent = totalSizeMB.toFixed(2) + ' MB';
                    
                    const audioList = document.getElementById('audioList');
                    
                    if (data.files.length === 0) {
                        audioList.innerHTML = `
                            <div class="no-files">
                                <div class="no-files-icon">🎵</div>
                                <h3>No audio files yet</h3>
                                <p>Use the API to generate and save audio files</p>
                            </div>
                        `;
                        return;
                    }
                    
                    audioList.innerHTML = data.files.map(file => `
                        <div class="audio-item" data-filename="${file.filename}">
                            <button class="play-btn" onclick="playAudio('${file.filename}', this)">▶️</button>
                            <div class="audio-info">
                                <div class="audio-name">${file.filename}</div>
                                <div class="audio-meta">
                                    ${file.size_mb} MB • Created: ${new Date(file.created).toLocaleString()}
                                </div>
                            </div>
                            <div class="audio-controls">
                                <button class="icon-btn" onclick="downloadAudio('${file.filename}')">⬇️</button>
                                <button class="icon-btn delete-btn" onclick="deleteAudio('${file.filename}')">🗑️</button>
                            </div>
                        </div>
                    `).join('');
                } catch (error) {
                    console.error('Failed to load library:', error);
                    alert('Failed to load audio library');
                }
            }
            
            function playAudio(filename, button) {
                const url = `/api/v1/library/${filename}`;
                const item = button.closest('.audio-item');
                
                // If clicking the same file, toggle play/pause
                if (currentPlaying === filename) {
                    if (audioPlayer.paused) {
                        audioPlayer.play();
                        button.textContent = '⏸️';
                    } else {
                        audioPlayer.pause();
                        button.textContent = '▶️';
                    }
                    return;
                }
                
                // Reset previous playing item
                if (currentPlaying) {
                    document.querySelectorAll('.audio-item').forEach(i => i.classList.remove('playing'));
                    document.querySelectorAll('.play-btn').forEach(b => b.textContent = '▶️');
                }
                
                // Play new audio
                currentPlaying = filename;
                audioPlayer.src = url;
                audioPlayer.classList.add('active');
                audioPlayer.play();
                button.textContent = '⏸️';
                item.classList.add('playing');
            }
            
            audioPlayer.onended = () => {
                document.querySelectorAll('.play-btn').forEach(b => b.textContent = '▶️');
                document.querySelectorAll('.audio-item').forEach(i => i.classList.remove('playing'));
                currentPlaying = null;
            };
            
            audioPlayer.onpause = () => {
                if (currentPlaying) {
                    const item = document.querySelector(`[data-filename="${currentPlaying}"]`);
                    if (item) {
                        item.querySelector('.play-btn').textContent = '▶️';
                    }
                }
            };
            
            audioPlayer.onplay = () => {
                if (currentPlaying) {
                    const item = document.querySelector(`[data-filename="${currentPlaying}"]`);
                    if (item) {
                        item.querySelector('.play-btn').textContent = '⏸️';
                    }
                }
            };
            
            function downloadAudio(filename) {
                window.open(`/api/v1/library/${filename}`, '_blank');
            }
            
            async function deleteAudio(filename) {
                if (!confirm(`Delete "${filename}"?`)) return;
                
                try {
                    const response = await fetch(`/api/v1/library/${filename}`, {
                        method: 'DELETE'
                    });
                    
                    if (response.ok) {
                        if (currentPlaying === filename) {
                            audioPlayer.pause();
                            audioPlayer.src = '';
                            currentPlaying = null;
                        }
                        loadLibrary();
                    } else {
                        alert('Failed to delete file');
                    }
                } catch (error) {
                    console.error('Failed to delete:', error);
                    alert('Failed to delete file');
                }
            }
            
            // Load library on page load
            loadLibrary();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/stream-player", response_class=HTMLResponse)
async def stream_player():
    """
    Interactive web page for testing WebSocket TTS streaming
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>gTTS WebSocket Streaming</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                padding: 40px;
                max-width: 600px;
                width: 100%;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 28px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 14px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                color: #555;
                font-weight: 500;
            }
            textarea {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 16px;
                font-family: inherit;
                resize: vertical;
                min-height: 120px;
                transition: border-color 0.3s;
            }
            textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            select {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 16px;
                background: white;
                cursor: pointer;
                transition: border-color 0.3s;
            }
            select:focus {
                outline: none;
                border-color: #667eea;
            }
            button {
                width: 100%;
                padding: 15px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            button:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
            }
            button:active:not(:disabled) {
                transform: translateY(0);
            }
            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            .status {
                margin-top: 20px;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
                display: none;
            }
            .status.show {
                display: block;
            }
            .status.info {
                background: #e3f2fd;
                color: #1976d2;
                border-left: 4px solid #1976d2;
            }
            .status.success {
                background: #e8f5e9;
                color: #388e3c;
                border-left: 4px solid #388e3c;
            }
            .status.error {
                background: #ffebee;
                color: #c62828;
                border-left: 4px solid #c62828;
            }
            .loader {
                display: inline-block;
                width: 14px;
                height: 14px;
                border: 2px solid rgba(0,0,0,0.1);
                border-radius: 50%;
                border-top-color: currentColor;
                animation: spin 0.8s linear infinite;
                margin-right: 8px;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔊 WebSocket TTS Streaming</h1>
            <p class="subtitle">Real-time text-to-speech via WebSocket</p>
            
            <form id="ttsForm">
                <div class="form-group">
                    <label for="text">Text to speak:</label>
                    <textarea 
                        id="text" 
                        placeholder="Enter text here..." 
                        required
                    >Hello! This is a test of the WebSocket text-to-speech streaming.</textarea>
                </div>
                
                <div class="form-group">
                    <label for="language">Language:</label>
                    <select id="language">
                        <option value="en">English</option>
                        <option value="sv">Swedish</option>
                        <option value="es">Spanish</option>
                        <option value="fr">French</option>
                        <option value="de">German</option>
                        <option value="it">Italian</option>
                        <option value="pt">Portuguese</option>
                        <option value="ja">Japanese</option>
                        <option value="zh">Chinese</option>
                        <option value="ar">Arabic</option>
                        <option value="ru">Russian</option>
                    </select>
                </div>
                
                <button type="submit" id="speakBtn">
                    🎤 Speak
                </button>
            </form>
            
            <div id="status" class="status"></div>
        </div>

        <script>
            let ws = null;
            let audioChunks = [];
            let isReceiving = false;
            
            const form = document.getElementById('ttsForm');
            const textInput = document.getElementById('text');
            const languageSelect = document.getElementById('language');
            const speakBtn = document.getElementById('speakBtn');
            const statusDiv = document.getElementById('status');
            
            function showStatus(message, type = 'info') {
                statusDiv.textContent = message;
                statusDiv.className = `status show ${type}`;
            }
            
            function showLoadingStatus(message) {
                statusDiv.innerHTML = `<span class="loader"></span>${message}`;
                statusDiv.className = 'status show info';
            }
            
            function connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws/tts`;
                
                ws = new WebSocket(wsUrl);
                
                ws.onopen = () => {
                    console.log('WebSocket connected');
                };
                
                ws.onmessage = async (event) => {
                    if (typeof event.data === 'string') {
                        const message = JSON.parse(event.data);
                        console.log('Received message:', message);
                        
                        if (message.status === 'generating') {
                            showLoadingStatus(message.message);
                            audioChunks = [];
                            isReceiving = false;
                        } else if (message.status === 'ready') {
                            showLoadingStatus('Streaming audio...');
                            isReceiving = true;
                        } else if (message.status === 'complete') {
                            showStatus('✓ Playing audio...', 'success');
                            playAudio();
                            speakBtn.disabled = false;
                        } else if (message.status === 'error') {
                            showStatus(`✗ Error: ${message.error}`, 'error');
                            speakBtn.disabled = false;
                        }
                    } else {
                        // Binary data (audio chunks)
                        if (isReceiving) {
                            const chunk = await event.data.arrayBuffer();
                            audioChunks.push(chunk);
                        }
                    }
                };
                
                ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    showStatus('✗ Connection error', 'error');
                    speakBtn.disabled = false;
                };
                
                ws.onclose = () => {
                    console.log('WebSocket closed');
                    ws = null;
                };
            }
            
            function playAudio() {
                if (audioChunks.length === 0) {
                    showStatus('✗ No audio data received', 'error');
                    return;
                }
                
                // Combine all chunks into one blob
                const blob = new Blob(audioChunks, { type: 'audio/mpeg' });
                const url = URL.createObjectURL(blob);
                
                // Create and play audio
                const audio = new Audio(url);
                audio.play().catch(error => {
                    console.error('Playback error:', error);
                    showStatus('✗ Playback error: ' + error.message, 'error');
                });
                
                audio.onended = () => {
                    URL.revokeObjectURL(url);
                    showStatus('✓ Playback complete', 'success');
                };
                
                audio.onerror = () => {
                    showStatus('✗ Audio playback failed', 'error');
                };
            }
            
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                
                const text = textInput.value.trim();
                const lang = languageSelect.value;
                
                if (!text) {
                    showStatus('✗ Please enter some text', 'error');
                    return;
                }
                
                if (!ws || ws.readyState !== WebSocket.OPEN) {
                    connectWebSocket();
                    // Wait a bit for connection to establish
                    setTimeout(() => {
                        if (ws && ws.readyState === WebSocket.OPEN) {
                            sendRequest(text, lang);
                        } else {
                            showStatus('✗ Failed to connect to server', 'error');
                        }
                    }, 500);
                } else {
                    sendRequest(text, lang);
                }
            });
            
            function sendRequest(text, lang) {
                speakBtn.disabled = true;
                showLoadingStatus('Connecting...');
                
                ws.send(JSON.stringify({
                    text: text,
                    lang: lang
                }));
            }
            
            // Connect on page load
            connectWebSocket();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
