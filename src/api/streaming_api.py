import numpy as np
from typing import Optional, Dict, Any, Generator, Iterator
from sseclient import SSEClient
from ..config import Config
from .base_api import BaseAPI
import requests
import json
from loguru import logger

class StreamingAPI(BaseAPI):
    """Streaming API implementation using Server-Sent Events"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key)
        self.config = Config.get_instance()
        self.base_url = base_url or self.config.api_base_url
        self._supported_languages = {}
        
    def transcribe_stream(self, audio: np.ndarray, language: Optional[str] = None) -> Iterator[str]:
        """Stream transcription results"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "text/event-stream"
        }
        logger.info(f"Making streaming API request to: {self.base_url}/transcribe/stream")
        logger.debug(f"Request headers: {headers}")
        
        # Save audio data to a temporary file
        import tempfile
        import soundfile as sf
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            # Save numpy array as WAV file
            sf.write(temp_file.name, audio, self.config.sample_rate)
            temp_path = temp_file.name
            logger.debug(f"Saved audio to temporary file: {temp_path}")
        
        try:
            # Prepare the file for upload
            with open(temp_path, 'rb') as audio_file:
                files = {
                    'audio': ('audio.wav', audio_file, 'audio/wav')
                }
                
                # Add other parameters
                data = {
                    'language': language,
                    'model': self.config.whisper_model,
                    'batch_size': self.config.batch_size
                }
                logger.debug(f"Request parameters: {data}")
                
                # Send request
                response = requests.post(
                    f"{self.base_url}/transcribe/stream",
                    headers=headers,
                    files=files,
                    data=data,
                    stream=True
                )
                response.raise_for_status()
                logger.info("Streaming connection established")
                
                # Process streaming response
                for line in response.iter_lines():
                    if line:
                        text = line.decode('utf-8')
                        logger.debug(f"Received raw data: {text}")
                        if text.startswith('data: '):
                            try:
                                # Try to parse as JSON
                                data = json.loads(text[6:])  # Remove 'data: ' prefix
                                logger.debug(f"Parsed JSON data: {data}")
                                if isinstance(data, dict):
                                    result = data.get("text", "")
                                    logger.info(f"Extracted text: {result}")
                                    yield result
                                else:
                                    yield str(data)
                            except json.JSONDecodeError as e:
                                logger.warning(f"Failed to parse JSON: {e}")
                                # If not JSON, yield the raw text
                                yield text[6:]
        except Exception as e:
            logger.error(f"Streaming API request failed: {str(e)}")
            logger.error(f"Response content: {response.content if 'response' in locals() else 'No response'}")
            raise
        finally:
            # Clean up the temporary file
            import os
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {e}")
    
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