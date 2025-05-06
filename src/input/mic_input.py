import numpy as np
import sounddevice as sd
from .base_input import BaseInput

class MicrophoneInput(BaseInput):
    """Class for handling microphone input"""
    
    def __init__(self, device=None, duration=None):
        super().__init__()
        self.device = device
        self.duration = duration  # Recording duration in seconds
        self._running = False
        self._stream = None
        self._audio_buffer = []
        
    def get_audio(self) -> np.ndarray:
        """Get recorded audio data"""
        if not self._audio_buffer:
            return np.array([])
        return np.concatenate(self._audio_buffer)
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio stream"""
        if status:
            print(f"Status: {status}")
        self._audio_buffer.append(indata.copy())
    
    def start(self):
        """Start recording from microphone"""
        if not self._running:
            self._audio_buffer = []
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=self._audio_callback,
                device=self.device
            )
            self._stream.start()
            self._running = True
    
    def stop(self):
        """Stop recording from microphone"""
        if self._running:
            self._stream.stop()
            self._stream.close()
            self._stream = None
            self._running = False
    
    @property
    def is_running(self) -> bool:
        return self._running 