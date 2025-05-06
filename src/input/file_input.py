import numpy as np
import soundfile as sf
from .base_input import BaseInput

class FileInput(BaseInput):
    """Class for handling audio file input"""
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self._running = False
        self._audio_data = None
        
    def get_audio(self) -> np.ndarray:
        """Read audio data from file"""
        if self._audio_data is None:
            self._audio_data, sample_rate = sf.read(self.file_path)
            if sample_rate != self.sample_rate:
                # TODO: Implement resampling if needed
                pass
        return self._audio_data
    
    def start(self):
        """Start reading from file"""
        self._running = True
        self.get_audio()
    
    def stop(self):
        """Stop reading from file"""
        self._running = False
        self._audio_data = None
    
    @property
    def is_running(self) -> bool:
        return self._running 