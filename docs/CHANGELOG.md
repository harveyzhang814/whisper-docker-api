# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Output format options
  - JSON format output (default)
  - Plain text output
  - Clipboard copy support
- Enhanced clipboard operation error handling
  - Handle clipboard access failures
  - Provide detailed error messages and potential causes
- API endpoints
  - GET /health - Health check endpoint
  - POST /transcribe - Audio transcription endpoint
  - POST /transcribe/stream - Streaming transcription endpoint
- Test coverage
  - Verified streaming API functionality
  - Added health check endpoint tests
  - Implemented SSE client testing
- Microphone input functionality
  - Complete recording with MicrophoneInput class
  - Real-time streaming with StreamingMicrophoneInput class
  - Device management utilities in BaseInput
  - Automatic and manual recording modes
- Test coverage for microphone functionality
  - Manual recording test script
  - Streaming integration tests
  - API endpoint tests

### Changed
- Added pyperclip dependency to client-requirements.txt
- Removed translation endpoints due to Whisper model limitations
- Updated Docker configuration to use port 8090
- Updated API documentation
  - Added authentication requirements and examples
  - Updated all endpoints with current implementation
  - Added security best practices
  - Enhanced troubleshooting guide

### Fixed
- Python package import issues in test scripts
- Environment variable handling in Docker deployment

### Security
- Implemented proper API key handling
- Added secure environment variable management

### Files Changed
- `client-requirements.txt`: Added pyperclip dependency
- `src/client.py`: Added output format handling and clipboard error handling
- `Dockerfile`: Updated port configuration
- `docker-compose.yml`: Added environment variable support
- `docs/api_guide.md`: Comprehensive update with current implementation 