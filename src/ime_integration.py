import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import requests
import queue
import threading
import time
from pathlib import Path
from typing import Optional
from loguru import logger
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv('.env.local')  # Try to load .env.local first
load_dotenv('.env')  # Fall back to .env if exists

class AudioCapture:
    def __init__(
        self,
        api_url: str = "http://localhost:5000",
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_duration: float = 2.0  # seconds
    ):
        self.api_url = api_url.rstrip("/")
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_duration = chunk_duration
        self.chunk_size = int(sample_rate * chunk_duration)
        
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.temp_dir = Path(tempfile.gettempdir()) / "whisper_ime"
        self.temp_dir.mkdir(exist_ok=True)
        
        logger.info(f"Initialized AudioCapture with sample rate: {sample_rate}Hz")

    def audio_callback(self, indata, frames, time, status):
        """Callback for audio stream."""
        if status:
            logger.warning(f"Audio callback status: {status}")
        self.audio_queue.put(indata.copy())

    def process_audio_chunk(self, audio_data: np.ndarray) -> Optional[str]:
        """Process a chunk of audio data and get transcription."""
        # Save audio chunk to temporary WAV file
        temp_file = self.temp_dir / f"chunk_{time.time()}.wav"
        sf.write(temp_file, audio_data, self.sample_rate)

        try:
            # Send to Whisper API
            with open(temp_file, "rb") as f:
                response = requests.post(
                    f"{self.api_url}/transcribe",
                    files={"audio": (temp_file.name, f, "audio/wav")}
                )
                response.raise_for_status()
                result = response.json()
                return result["text"].strip()
        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}")
            return None
        finally:
            temp_file.unlink()

    def process_audio_queue(self):
        """Process audio chunks from the queue."""
        while self.is_recording:
            try:
                audio_data = self.audio_queue.get(timeout=1.0)
                if audio_data is not None:
                    text = self.process_audio_chunk(audio_data)
                    if text:
                        print(f"Transcription: {text}")
                        # Here you would integrate with the OS input method
                        # For example, using pyautogui to type the text
                        # or using platform-specific APIs
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing audio queue: {e}")

    def start_recording(self):
        """Start recording audio from microphone."""
        self.is_recording = True
        
        # Start processing thread
        self.process_thread = threading.Thread(target=self.process_audio_queue)
        self.process_thread.start()

        # Start audio stream
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=self.audio_callback,
                blocksize=self.chunk_size
            ):
                logger.info("Started recording. Press Ctrl+C to stop.")
                while self.is_recording:
                    time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in audio stream: {e}")
            self.stop_recording()

    def stop_recording(self):
        """Stop recording audio."""
        self.is_recording = False
        if hasattr(self, 'process_thread'):
            self.process_thread.join()
        logger.info("Stopped recording")

def main():
    """Main function to run the IME integration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Whisper IME Integration")
    parser.add_argument("--url", default="http://localhost:5000", help="Whisper API URL")
    parser.add_argument("--sample-rate", type=int, default=16000, help="Audio sample rate")
    parser.add_argument("--channels", type=int, default=1, help="Audio channels")
    parser.add_argument("--chunk-duration", type=float, default=2.0, help="Audio chunk duration in seconds")
    
    args = parser.parse_args()
    
    capture = AudioCapture(
        api_url=args.url,
        sample_rate=args.sample_rate,
        channels=args.channels,
        chunk_duration=args.chunk_duration
    )
    
    try:
        capture.start_recording()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        capture.stop_recording()

if __name__ == "__main__":
    main() 