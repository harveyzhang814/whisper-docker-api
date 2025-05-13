# Whisper API Guide

> **Note:** Docker API environment variables are now managed independently in `.env.docker.local` and `.env.docker.example` under the `docker_api/` directory. Please refer to these files for deployment configuration.

## Docker API Deployment (Recommended)

- All Docker API related files, configs, and source code are in the `docker_api/` directory.
- Environment variables for Docker API are managed in `docker_api/.env.docker.local` and `.env.docker.example`.
- To build and deploy the API service, run the following in the project root:

```bash
docker-compose -f docker_api/docker-compose.yml up --build -d
```
- To view logs:
```bash
docker-compose -f docker_api/docker-compose.yml logs -f
```
- To stop the service:
```bash
docker-compose -f docker_api/docker-compose.yml down
```

---

This document provides detailed information about the Whisper Transcription API endpoints, their usage, and examples.

## Base URL

```
http://localhost:8090
```

## Authentication

The API requires authentication using an API key. Include the API key in the request headers:

```
Authorization: Bearer YOUR_API_KEY
```

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
- Headers:
  - `Authorization: Bearer YOUR_API_KEY`
- Body Parameters:
  - `audio` (required): Audio file
    - Supported formats: WAV, MP3, OGG, FLAC, M4A
    - Recommended: WAV, 16kHz, mono
  - `format` (optional): Response format
    - Values: `json` (default) | `text` | `clipboard`
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
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "audio=@sample/audio/test.wav" \
  http://localhost:8090/transcribe

# Text-only response
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "audio=@sample/audio/test.wav" \
  -F "format=text" \
  http://localhost:8090/transcribe
```

### 3. Streaming Transcription

Get real-time transcription results as the audio is processed.

```http
POST /transcribe/stream
```

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Headers:
  - `Authorization: Bearer YOUR_API_KEY`
  - `Accept: text/event-stream` (for SSE)
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
curl -N -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Accept: text/event-stream" \
  -F "audio=@sample/audio/test.wav" \
  http://localhost:8090/transcribe/stream
```

**Example (Python):**
```python
import requests
from sseclient import SSEClient

def stream_audio(file_path, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "text/event-stream"
    }
    
    with open(file_path, 'rb') as f:
        files = {'audio': f}
        response = requests.post(
            'http://localhost:8090/transcribe/stream',
            headers=headers,
            files=files,
            stream=True
        )
        client = SSEClient(response)
        for event in client.events():
            print(event.data)

stream_audio('sample/audio/test.wav', 'YOUR_API_KEY')
```

## Error Handling

The API uses standard HTTP status codes:

- 200: Success
- 400: Bad Request (invalid parameters)
- 401: Unauthorized (invalid or missing API key)
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
   - Use streaming endpoint for long audio files

3. **Performance:**
   - Keep audio segments under 30 seconds for best results
   - Use appropriate model size for your needs
   - Consider batch processing for multiple files

4. **Security:**
   - Keep your API key secure
   - Use HTTPS in production
   - Implement rate limiting

## Client Integration

### Python Client Example

```python
from src.api.standard_api import StandardAPI
from src.api.streaming_api import StreamingAPI

# Standard API usage
api = StandardAPI(api_key="YOUR_API_KEY")
result = api.transcribe("sample/audio/test.wav")
print(result)

# Streaming API usage
streaming_api = StreamingAPI(api_key="YOUR_API_KEY")
for text in streaming_api.transcribe_stream("sample/audio/test.wav"):
    print(text)
```

### JavaScript Client Example

```javascript
async function transcribe(audioFile, apiKey) {
    const formData = new FormData();
    formData.append('audio', audioFile);

    const response = await fetch('http://localhost:8090/transcribe', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${apiKey}`
        },
        body: formData
    });

    return await response.json();
}

async function streamTranscribe(audioFile, apiKey) {
    const formData = new FormData();
    formData.append('audio', audioFile);

    const response = await fetch('http://localhost:8090/transcribe/stream', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Accept': 'text/event-stream'
        },
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
   - Verify the service is running: `curl http://localhost:8090/health`
   - Check Docker container status: `docker-compose ps`
   - Check logs: `docker-compose logs whisper-server`

2. **Authentication Issues:**
   - Verify your API key is correct
   - Check if the API key is properly set in the request headers
   - Ensure the API key has not expired

3. **Audio Issues:**
   - Verify audio format: `ffprobe your_audio.wav`
   - Convert audio if needed: `ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav`

4. **Performance Issues:**
   - Check Docker resource allocation
   - Monitor system resources
   - Consider using a smaller model
   - Use streaming endpoint for large files

## Support

For issues and feature requests, please create an issue in the GitHub repository. 