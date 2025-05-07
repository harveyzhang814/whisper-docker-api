import numpy as np
import sounddevice as sd
import time
from typing import Optional
from .base_input import BaseInput

class MicrophoneInput(BaseInput):
    """Class for handling complete microphone recording"""
    
    def __init__(self, device: Optional[int] = None, duration: Optional[float] = None):
        """Initialize microphone input for complete recording
        
        Args:
            device: Audio device index
            duration: Recording duration in seconds (None for manual stop)
            
        Raises:
            RuntimeError: If no microphone is available or specified device is not available
        """
        super().__init__()
        
        # Check microphone availability
        if not self.is_microphone_available(device):
            if device is not None:
                raise RuntimeError(f"Microphone device {device} is not available")
            else:
                raise RuntimeError("No microphone is available")
        
        self.device = device if device is not None else self.get_default_microphone()
        self.duration = duration
        self._running = False
        self._stream = None
        self._audio_buffer = []
        self._start_time = None
    
    def get_audio(self) -> np.ndarray:
        """Get complete recorded audio data
        
        Returns:
            numpy.ndarray: Complete audio recording as a numpy array
        """
        if not self._audio_buffer:
            return np.array([])
        return np.concatenate(self._audio_buffer)
    
    def _audio_callback(self, indata: np.ndarray, frames: int, 
                       time_info: dict, status: sd.CallbackFlags) -> None:
        """Internal callback for audio recording"""
        if status:
            print(f"Status: {status}")
        self._audio_buffer.append(indata.copy())
        
        # Stop recording if duration is reached
        if self.duration is not None and self._start_time is not None:
            elapsed = time.time() - self._start_time
            print(f"Elapsed time: {elapsed:.2f}s / {self.duration}s")
            if elapsed >= self.duration:
                print("Duration reached, stopping recording...")
                self.stop()
    
    def start(self) -> None:
        """Start recording from microphone"""
        if not self._running:
            self._audio_buffer = []
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=self._audio_callback,
                device=self.device
            )
            self._start_time = time.time()
            self._stream.start()
            self._running = True
    
    def stop(self) -> None:
        """Stop recording from microphone"""
        try:
            if self._running:
                print("Stopping recording...")
                if self._stream is not None:
                    self._stream.stop()
                    self._stream.close()
                self._stream = None
                self._running = False
                print("Recording stopped successfully")
        except Exception as e:
            print(f"Error stopping recording: {e}")
            self._stream = None
            self._running = False
    
    @property
    def is_running(self) -> bool:
        """Check if recording is active"""
        return self._running
    
    def save_to_file(self, filename: str) -> None:
        """Save recorded audio to a file
        
        Args:
            filename: Path to save the audio file
        """
        audio_data = self.get_audio()
        if len(audio_data) > 0:
            import soundfile as sf
            sf.write(filename, audio_data, self.sample_rate) 