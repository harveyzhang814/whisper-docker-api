import os
import numpy as np
import soundfile as sf
from typing import Optional
from .base_input import BaseInput
from ..utils.audio_utils import AudioUtils
from loguru import logger

class FileInput(BaseInput):
    """Class for handling audio file input"""
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self._running = False
        self._audio_data = None
        self._temp_wav_path: Optional[str] = None
        
    def get_audio(self) -> np.ndarray:
        """Read audio data from file and convert to Whisper format"""
        if self._audio_data is None:
            try:
                # Convert to Whisper format if needed
                self._temp_wav_path = AudioUtils.convert_to_whisper_format(
                    self.file_path,
                    overwrite=True
                )
                logger.debug(f"Converted audio to Whisper format: {self._temp_wav_path}")
                
                # Load the converted audio
                self._audio_data, _ = AudioUtils.load_audio(
                    self._temp_wav_path,
                    normalize=True
                )
                logger.debug("Audio loaded and normalized")
                
            except Exception as e:
                logger.error(f"Failed to process audio file: {str(e)}")
                raise
                
        return self._audio_data
    
    def start(self):
        """Start reading from file"""
        self._running = True
        self.get_audio()
    
    def stop(self):
        """Stop reading from file and cleanup"""
        self._running = False
        self._audio_data = None
        
        # Cleanup temporary WAV file
        if self._temp_wav_path and os.path.exists(self._temp_wav_path):
            try:
                if self._temp_wav_path != self.file_path:  # Don't delete if it's the original file
                    os.unlink(self._temp_wav_path)
                    logger.debug(f"Deleted temporary WAV file: {self._temp_wav_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary WAV file: {str(e)}")
        self._temp_wav_path = None
    
    @property
    def is_running(self) -> bool:
        """Check if input is running"""
        return self._running 