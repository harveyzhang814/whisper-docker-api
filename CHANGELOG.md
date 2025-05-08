# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Added `HotkeyListener` utility class in `src/utils/hotkey_listener.py` using `pynput` to listen for `ctrl+r` on macOS. When detected, stops listening and prints a log message.
- Created `src/feature/` directory for organizing self-contained feature modules.
### Changed
- Split dependencies: API/server dependencies are now only in `requirements.txt`, client dependencies are only in `client-requirements.txt`.
- Removed `pyperclip` and `sseclient-py` from `requirements.txt` (now only in client-requirements.txt).
- Removed API/server-only dependencies (such as `fastapi`, `uvicorn`, `openai-whisper`, `torch`, `pydantic`, `tqdm`, `pyaudio`, `python-multipart`) from `client-requirements.txt`.
- Both files retain shared dependencies (`numpy`, `sounddevice`, `soundfile`, `requests`, `python-dotenv`, `loguru`) for environment independence. 