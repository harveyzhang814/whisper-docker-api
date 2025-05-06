import numpy as np
from typing import Optional, Dict, Any
import requests
from ..config import Config
from .base_api import BaseAPI

class StandardAPI(BaseAPI):
    """Standard synchronous API implementation"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key)
        self.config = Config.get_instance()
        self.base_url = base_url or self.config.api_base_url
        self._supported_languages = {}  # Cache for supported languages
        
    def transcribe(self, audio: np.ndarray, language: Optional[str] = None) -> str:
        """Transcribe audio using standard API call"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {
            "audio": audio.tobytes(),
            "language": language,
            "model": self.config.whisper_model,
            "batch_size": self.config.batch_size
        }
        
        response = requests.post(
            f"{self.base_url}/transcribe",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["text"]
    
    def translate(self, text: str, target_language: str) -> str:
        """Translate text using standard API call"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {
            "text": text,
            "target_language": target_language,
            "model": self.config.whisper_model
        }
        
        response = requests.post(
            f"{self.base_url}/translate",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["translated_text"]
    
    @property
    def supported_languages(self) -> Dict[str, str]:
        """Get supported languages from API"""
        if not self._supported_languages:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(
                f"{self.base_url}/languages",
                headers=headers
            )
            response.raise_for_status()
            self._supported_languages = response.json()
        return self._supported_languages
    
    def configure(self, **kwargs: Any) -> None:
        """Configure API settings"""
        for key, value in kwargs.items():
            setattr(self, key, value) 