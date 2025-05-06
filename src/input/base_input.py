from abc import ABC, abstractmethod
import numpy as np

class BaseInput(ABC):
    """Base class for all input sources"""
    
    def __init__(self):
        self.sample_rate = 16000  # Default sample rate for Whisper
        
    @abstractmethod
    def get_audio(self) -> np.ndarray:
        """Get audio data as numpy array"""
        pass
    
    @abstractmethod
    def start(self):
        """Start the input source"""
        pass
    
    @abstractmethod
    def stop(self):
        """Stop the input source"""
        pass
    
    @property
    def is_running(self) -> bool:
        """Check if the input source is running"""
        pass 