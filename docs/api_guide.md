# Whisper API Guide

This document provides detailed information about the Whisper Transcription API endpoints, their usage, and examples.

## Base URL

```
http://localhost:9000
```

## Authentication

Currently, the API does not require authentication. However, it's recommended to run the service behind a reverse proxy with proper security measures in production.

## API Endpoints

### 1. Health Check

Check if the service is running and get model information.

```http
GET /health
```

**Response:**
```json
{
    "status": "healthy",
    "model": "small",
    "version": "1.0.0"
}
```

### 2. Audio Transcription

Convert audio to text with detailed segmentation.

```http
POST /transcribe
```

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body Parameters:
  - `audio` (required): Audio file
    - Supported formats: WAV, MP3, OGG, FLAC, M4A
    - Recommended: WAV, 16kHz, mono
  - `format` (optional): Response format
    - Values: `json` (default) | `text`
  - `language` (optional): Source language
    - Format: ISO 639-1 code (e.g., "en", "zh")
    - Default: Auto-detect

**Response (JSON):**
```json
{
    "text": "Complete transcription text",
    "segments": [
        {
            "start": 0.0,
            "end": 2.5,
            "text": "First segment"
        },
        {
            "start": 2.5,
            "end": 5.0,
            "text": "Second segment"
        }
    ],
    "language": "en"
}
```

**Response (Text):**
```
Complete transcription text
```

**Example (curl):**
```bash
# JSON response
curl -X POST -F "audio=@sample/audio/test.wav" http://localhost:9000/transcribe

# Text-only response
curl -X POST -F "audio=@sample/audio/test.wav" -F "format=text" http://localhost:9000/transcribe
```

### 3. Streaming Transcription

Get real-time transcription results as the audio is processed.

```http
POST /transcribe/stream
```

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body Parameters:
  - `audio` (required): Audio file or stream
  - `language` (optional): Source language

**Response:**
Server-Sent Events (SSE) with incremental transcriptions:
```
data: {"text": "First part of speech"}

data: {"text": "Second part of speech"}

data: {"text": "Final part of speech"}
```

**Example (curl):**
```bash
curl -N -X POST -F "audio=@sample/audio/test.wav" http://localhost:9000/transcribe/stream
```

**Example (Python):**
```python
import requests

def stream_audio(file_path):
    with open(file_path, 'rb') as f:
        response = requests.post(
            'http://localhost:9000/transcribe/stream',
            files={'audio': f},
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                print(line.decode('utf-8'))

stream_audio('sample/audio/test.wav')
```

## Error Handling

The API uses standard HTTP status codes:

- 200: Success
- 400: Bad Request (invalid parameters)
- 415: Unsupported Media Type
- 500: Internal Server Error

Error Response Format:
```json
{
    "error": "Error message",
    "detail": "Detailed error information"
}
```

## Best Practices

1. **Audio Format:**
   - Use WAV format when possible
   - Sample rate: 16kHz
   - Channels: Mono
   - Bit depth: 16-bit

2. **File Size:**
   - Recommended maximum: 25MB
   - For longer audio, split into chunks
   - Stream long audio files

3. **Performance:**
   - Keep audio segments under 30 seconds for best results
   - Use appropriate model size for your needs
   - Consider batch processing for multiple files

4. **Rate Limiting:**
   - Implement appropriate rate limiting in production
   - Consider using a queue system for batch processing

## Client Integration

### Python Client Example

```python
import requests

class WhisperClient:
    def __init__(self, base_url="http://localhost:9000"):
        self.base_url = base_url.rstrip("/")

    def transcribe(self, audio_path, format="json"):
        with open(audio_path, "rb") as f:
            response = requests.post(
                f"{self.base_url}/transcribe",
                files={"audio": f},
                data={"format": format}
            )
            response.raise_for_status()
            return response.json()

    def stream_transcribe(self, audio_path):
        with open(audio_path, "rb") as f:
            response = requests.post(
                f"{self.base_url}/transcribe/stream",
                files={"audio": f},
                stream=True
            )
            for line in response.iter_lines():
                if line:
                    yield line.decode("utf-8")
```

### JavaScript Client Example

```javascript
async function transcribe(audioFile) {
    const formData = new FormData();
    formData.append('audio', audioFile);

    const response = await fetch('http://localhost:9000/transcribe', {
        method: 'POST',
        body: formData
    });

    return await response.json();
}

async function streamTranscribe(audioFile) {
    const formData = new FormData();
    formData.append('audio', audioFile);

    const response = await fetch('http://localhost:9000/transcribe/stream', {
        method: 'POST',
        body: formData
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const {value, done} = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        console.log(text);
    }
}
```

## Troubleshooting

1. **Connection Issues:**
   - Verify the service is running: `curl http://localhost:9000/health`
   - Check Docker container status: `docker-compose ps`
   - Check logs: `docker-compose logs whisper-server`

2. **Audio Issues:**
   - Verify audio format: `ffprobe your_audio.wav`
   - Convert audio if needed: `ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav`

3. **Performance Issues:**
   - Check Docker resource allocation
   - Monitor system resources
   - Consider using a smaller model

## Support

For issues and feature requests, please create an issue in the GitHub repository. 