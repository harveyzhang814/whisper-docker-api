# Whisper Translation Server

A real-time speech-to-text service using OpenAI's Whisper model, optimized for Apple Silicon (ARM64) and containerized with Docker.

## Features

- 🎙️ Real-time audio transcription using OpenAI Whisper
- 🐳 Containerized deployment with Docker
- 🚀 FastAPI server with streaming support
- 🔌 Easy integration with input methods
- 💻 Optimized for Apple Silicon (M-series) processors
- 🌐 RESTful API for audio transcription
- 📱 Real-time microphone input support
- 🔧 Configurable audio settings

## System Requirements

- macOS with Apple Silicon (M1/M2/M3)
- Docker Desktop for Apple Silicon
- Python 3.10 or higher
- ffmpeg (installed automatically in Docker)

## Project Structure

```
whisper-translation/
├── src/
│   ├── app.py           # FastAPI server implementation
│   ├── client.py        # API client for testing
│   └── ime_integration.py # Real-time microphone integration
├── config/
│   └── logging.conf     # Logging configuration
├── docs/
│   └── api_guide.md     # API documentation
├── sample/
│   └── audio/          # Sample audio files for testing
├── tests/
│   └── test_api.py     # API tests
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
├── requirements.txt    # Server dependencies
├── client-requirements.txt # Client dependencies
└── .env.example       # Example environment variables
```

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/whisper-translation.git
   cd whisper-translation
   ```

2. Copy and configure environment variables:
   ```bash
   cp .env.example .env.local  # For local development
   # or
   cp .env.example .env       # For production
   ```

3. Start the Docker service:
   ```bash
   docker-compose up -d
   ```

4. Test the API:
   ```bash
   curl -X POST -F "audio=@sample/audio/test.wav" http://localhost:9000/transcribe
   ```

## Client Setup (Optional)

If you want to use the real-time microphone input feature:

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install client dependencies:
   ```bash
   pip3 install -r client-requirements.txt
   ```

3. Grant microphone permissions:
   - System Settings > Privacy & Security > Microphone
   - Enable for Terminal/IDE

4. Run the microphone integration:
   ```bash
   python3 src/ime_integration.py --url http://localhost:9000
   ```

## Configuration

### Environment Variables (.env.local or .env)

- `WHISPER_MODEL`: Model size (tiny/base/small/medium/large)
- `API_HOST`: Server host (default: 0.0.0.0)
- `API_PORT`: Server port (default: 9000)
- `BATCH_SIZE`: Inference batch size (default: 16)

Note: `.env.local` takes precedence over `.env` and is ignored by Git.

### Audio Settings

- Sample Rate: 16kHz (recommended)
- Channels: Mono
- Format: WAV (recommended), MP3, OGG supported
- Chunk Duration: 2 seconds (configurable)

## API Endpoints

### POST /transcribe

Transcribe an audio file.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: 
  - audio: Audio file
  - format: Output format (json/text)

**Response:**
```json
{
    "text": "Transcribed text",
    "segments": [
        {
            "start": 0.0,
            "end": 2.5,
            "text": "Segment text"
        }
    ]
}
```

### POST /transcribe/stream

Stream transcription results in real-time.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body:
  - audio: Audio file or stream

**Response:**
Server-Sent Events (SSE) with transcription updates.

## Performance Optimization

- Model Selection Guide:
  - tiny: Fastest, lowest accuracy (1GB VRAM)
  - base: Good balance (1GB VRAM)
  - small: Better accuracy (2GB VRAM)
  - medium: High accuracy (5GB VRAM)
  - large: Best accuracy (10GB VRAM)

- Docker Resource Allocation:
  - Recommended minimum: 2GB RAM
  - Recommended CPU: 2 cores
  - GPU acceleration supported if available

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Building Docker Image
```bash
docker-compose build
```

### Local Development
```bash
uvicorn src.app:app --reload --host 0.0.0.0 --port 9000
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Docker](https://www.docker.com/) 