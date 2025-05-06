import numpy as np
from typing import Optional, Dict, Any, Generator, Iterator
from sseclient import SSEClient
from ..config import Config
from .base_api import BaseAPI

class StreamingAPI(BaseAPI):
    """Streaming API implementation using Server-Sent Events"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key)
        self.config = Config.get_instance()
        self.base_url = base_url or self.config.api_base_url
        self._supported_languages = {}
        
    def transcribe_stream(self, audio: np.ndarray, language: Optional[str] = None) -> Iterator[str]:
        """Stream transcription results"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {
            "audio": audio.tobytes(),
            "language": language,
            "model": self.config.whisper_model,
            "batch_size": self.config.batch_size
        }
        
        messages = SSEClient(
            f"{self.base_url}/transcribe/stream",
            headers=headers,
            data=data
        )
        
        for msg in messages:
            if msg.data:
                yield msg.data
    
    def translate_stream(self, text: str, target_language: str) -> Iterator[str]:
        """Stream translation results"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {
            "text": text,
            "target_language": target_language,
            "model": self.config.whisper_model
        }
        
        messages = SSEClient(
            f"{self.base_url}/translate/stream",
            headers=headers,
            data=data
        )
        
        for msg in messages:
            if msg.data:
                yield msg.data
    
    def transcribe(self, audio: np.ndarray, language: Optional[str] = None) -> str:
        """Collect all streaming transcription results"""
        return "".join(self.transcribe_stream(audio, language))
    
    def translate(self, text: str, target_language: str) -> str:
        """Collect all streaming translation results"""
        return "".join(self.translate_stream(text, target_language))
    
    @property
    def supported_languages(self) -> Dict[str, str]:
        """Get supported languages from API"""
        if not self._supported_languages:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            messages = SSEClient(
                f"{self.base_url}/languages/stream",
                headers=headers
            )
            for msg in messages:
                if msg.data:
                    self._supported_languages.update(msg.data)
        return self._supported_languages
    
    def configure(self, **kwargs: Any) -> None:
        """Configure API settings"""
        for key, value in kwargs.items():
            setattr(self, key, value) 