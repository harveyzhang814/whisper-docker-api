import numpy as np
import sounddevice as sd
from typing import Callable, Optional
from .base_input import BaseInput

class StreamingMicrophoneInput(BaseInput):
    """Class for handling real-time streaming microphone input"""
    
    def __init__(self, 
                 device: Optional[int] = None,
                 chunk_size: int = 1024,
                 callback: Optional[Callable[[np.ndarray], None]] = None):
        """Initialize streaming microphone input
        
        Args:
            device: Audio device index
            chunk_size: Size of audio chunks to process
            callback: Callback function to process audio chunks in real-time
            
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
        self.chunk_size = chunk_size
        self.callback = callback
        self._running = False
        self._stream = None
    
    def _audio_callback(self, indata: np.ndarray, frames: int, 
                       time_info: dict, status: sd.CallbackFlags) -> None:
        """Callback for audio stream processing"""
        if status:
            print(f"Status: {status}")
        
        # Process the audio chunk
        if self.callback:
            self.callback(indata.copy())
    
    def start(self) -> None:
        """Start streaming from microphone"""
        if not self._running:
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=self._audio_callback,
                device=self.device,
                blocksize=self.chunk_size
            )
            self._stream.start()
            self._running = True
    
    def stop(self) -> None:
        """Stop streaming from microphone"""
        if self._running:
            self._stream.stop()
            self._stream.close()
            self._stream = None
            self._running = False
    
    @property
    def is_running(self) -> bool:
        """Check if streaming is active"""
        return self._running 