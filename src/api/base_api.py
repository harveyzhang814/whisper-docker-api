from abc import ABC, abstractmethod
import numpy as np
from typing import Optional, Dict, Any

class BaseAPI(ABC):
    """Base class for API interactions"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        
    @abstractmethod
    def transcribe(self, audio: np.ndarray, language: Optional[str] = None) -> str:
        """Transcribe audio to text"""
        pass
    
    @abstractmethod
    def translate(self, text: str, target_language: str) -> str:
        """Translate text to target language"""
        pass
    
    @property
    @abstractmethod
    def supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported languages"""
        pass
    
    @abstractmethod
    def configure(self, **kwargs: Any) -> None:
        """Configure API settings"""
        pass 