# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Added `HotkeyListener` utility class in `src/utils/hotkey_listener.py` using `pynput` to listen for `ctrl+r` on macOS. When detected, stops listening and prints a log message.
- Created `src/feature/` directory for organizing self-contained feature modules.
- Unified configuration system with Docker API support
- Docker API specific configuration options
- Template environment file for Docker configuration
- Generated python_api/requirements.txt including all dependencies from client-requirements.txt for unified backend and client dependency management.
- Created swift_ui directory for SwiftUI frontend code and documentation.
### Changed
- Split dependencies: API/server dependencies are now only in `requirements.txt`, client dependencies are only in `client-requirements.txt`.
- Removed `pyperclip` and `sseclient-py` from `requirements.txt` (now only in client-requirements.txt).
- Removed API/server-only dependencies (such as `fastapi`, `uvicorn`, `openai-whisper`, `torch`, `pydantic`, `tqdm`, `pyaudio`, `python-multipart`) from `client-requirements.txt`.
- Both files retain shared dependencies (`numpy`, `sounddevice`, `soundfile`, `requests`, `python-dotenv`, `loguru`) for environment independence.
- Migrated all Docker API related files to `docker_api/` directory for monorepo management.
- Docker API environment variables are now managed independently in `docker_api/.env.docker.local` and `docker_api/.env.docker.example`.
- Updated `docker-compose.yml`, `Dockerfile`, and `config.py` to use the new env files and paths.
- Updated documentation to reflect the new structure and configuration method.
- Refactored configuration loading mechanism to support multiple environment files
- Enhanced config class with Docker-specific properties
### Fixed
- Improved configuration file path handling using Path objects
- Standardized environment variable loading order
- Fixed all imports from `src.config` to `config.config` for unified configuration management 