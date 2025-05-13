from abc import ABC, abstractmethod
import numpy as np
from typing import Optional, Dict, Any

class BaseAPI(ABC):
    """Base class for API interactions
    
    This class defines the base interface for audio transcription API interactions.
    Implementations should provide concrete implementations of the abstract methods.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        
    @abstractmethod
    def transcribe(self, audio: np.ndarray, language: Optional[str] = None) -> str:
        """Transcribe audio to text
        
        Args:
            audio: Audio data as numpy array
            language: Optional source language code
            
        Returns:
            str: Transcribed text
        """
        pass
    
    @property
    @abstractmethod
    def supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported languages
        
        Returns:
            Dict[str, str]: Dictionary mapping language codes to names
        """
        pass
    
    @abstractmethod
    def configure(self, **kwargs: Any) -> None:
        """Configure API settings
        
        Args:
            **kwargs: Configuration key-value pairs
        """
        pass 