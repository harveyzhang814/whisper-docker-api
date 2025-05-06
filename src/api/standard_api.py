import numpy as np
from typing import Optional, Dict, Any
import requests
from src.config import Config
from .base_api import BaseAPI
from loguru import logger
from src.utils.audio_utils import AudioUtils
import tempfile
import soundfile as sf
import os

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
        logger.info(f"Making API request to: {self.base_url}/transcribe")
        logger.debug(f"Request headers: {headers}")
        
        # Save audio data to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            # Save original audio to temporary file
            sf.write(temp_file.name, audio, self.config.sample_rate)
            temp_path = temp_file.name
            logger.debug(f"Saved original audio to temporary file: {temp_path}")
            
            try:
                # Check if the audio meets Whisper requirements
                audio_info = AudioUtils.get_audio_info(temp_path)
                meets_requirements = (
                    audio_info['sample_rate'] == AudioUtils.WHISPER_SAMPLE_RATE and
                    audio_info['channels'] == AudioUtils.WHISPER_CHANNELS and
                    (audio_info['bit_depth'] == 0 or  # Some formats don't report bit depth
                     audio_info['bit_depth'] == AudioUtils.WHISPER_BIT_DEPTH)
                )
                
                # Use original file or convert as needed
                if meets_requirements:
                    logger.debug("Audio already meets Whisper format requirements")
                    whisper_audio_path = temp_path
                else:
                    logger.debug(f"Converting audio to Whisper format (current format: {audio_info})")
                    whisper_audio_path = AudioUtils.convert_to_whisper_format(
                        temp_path,
                        overwrite=True
                    )
                
                # Prepare the file for upload
                with open(whisper_audio_path, 'rb') as audio_file:
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
                        f"{self.base_url}/transcribe",
                        headers=headers,
                        files=files,
                        data=data
                    )
                    response.raise_for_status()
                    
                    # Parse response
                    result = response.json()
                    logger.info(f"API Response: {result}")
                    if isinstance(result, dict):
                        return result.get("text", "")  # Get text field or empty string
                    return str(result)  # Fallback: convert response to string
                    
            except Exception as e:
                logger.error(f"API request failed: {str(e)}")
                logger.error(f"Response content: {response.content if 'response' in locals() else 'No response'}")
                raise
            finally:
                # Clean up the temporary files
                try:
                    os.unlink(temp_path)
                    if temp_path != whisper_audio_path:  # If paths are different, clean up converted file too
                        os.unlink(whisper_audio_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file(s): {e}")
    
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