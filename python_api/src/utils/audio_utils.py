import os
import subprocess
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Union, Tuple, Optional
from loguru import logger

class AudioUtils:
    """Audio format conversion utilities"""
    
    WHISPER_SAMPLE_RATE = 16000
    WHISPER_CHANNELS = 1
    WHISPER_BIT_DEPTH = 16
    
    @staticmethod
    def convert_to_whisper_format(
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        overwrite: bool = False
    ) -> str:
        """Convert audio file to Whisper model format requirements
        
        Args:
            input_path: Path to input audio file
            output_path: Path to save converted audio file (optional)
            overwrite: Whether to overwrite existing output file
            
        Returns:
            str: Path to converted audio file
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            RuntimeError: If ffmpeg conversion fails
        """
        input_path = str(input_path)
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        # If output path not specified, create one with a temporary name
        if output_path is None:
            output_dir = str(Path(input_path).parent)
            temp_name = f"temp_{Path(input_path).stem}.wav"
            output_path = str(Path(output_dir) / temp_name)
        else:
            output_path = str(output_path)
            
        # Check if input file already meets requirements
        try:
            audio_info = AudioUtils.get_audio_info(input_path)
            meets_requirements = (
                audio_info['sample_rate'] == AudioUtils.WHISPER_SAMPLE_RATE and
                audio_info['channels'] == AudioUtils.WHISPER_CHANNELS and
                (audio_info['bit_depth'] == 0 or  # Some formats don't report bit depth
                 audio_info['bit_depth'] == AudioUtils.WHISPER_BIT_DEPTH)
            )
            
            if meets_requirements:
                logger.debug("Audio already meets Whisper format requirements")
                if input_path != output_path:
                    # Copy file if different path
                    import shutil
                    shutil.copy2(input_path, output_path)
                return output_path
                
        except Exception as e:
            logger.warning(f"Failed to check audio format: {e}, proceeding with conversion")
            
        try:
            # Construct ffmpeg command
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-ar', str(AudioUtils.WHISPER_SAMPLE_RATE),  # Sample rate
                '-ac', str(AudioUtils.WHISPER_CHANNELS),     # Channels
                '-c:a', 'pcm_s16le',                        # 16-bit PCM encoding
                '-y' if overwrite else '-n',                # Overwrite flag
                output_path
            ]
            
            # Run ffmpeg
            logger.info(f"Converting audio: {input_path} -> {output_path}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg conversion failed: {result.stderr}")
                
            logger.info("Audio conversion completed successfully")
            return output_path
            
        except Exception as e:
            logger.error(f"Audio conversion failed: {str(e)}")
            raise
    
    @staticmethod
    def load_audio(
        file_path: Union[str, Path],
        normalize: bool = True
    ) -> Tuple[np.ndarray, int]:
        """Load audio file and ensure it meets Whisper format requirements
        
        Args:
            file_path: Path to audio file
            normalize: Whether to normalize audio data
            
        Returns:
            Tuple[np.ndarray, int]: Audio data and sample rate
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = str(file_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
            
        try:
            # Load audio file
            audio, sample_rate = sf.read(file_path)
            
            # Convert to mono if stereo
            if len(audio.shape) > 1:
                logger.debug("Converting stereo to mono")
                audio = audio.mean(axis=1)
            
            # Resample if needed
            if sample_rate != AudioUtils.WHISPER_SAMPLE_RATE:
                logger.debug(f"Resampling from {sample_rate}Hz to {AudioUtils.WHISPER_SAMPLE_RATE}Hz")
                from scipy import signal
                audio = signal.resample(
                    audio,
                    int(len(audio) * AudioUtils.WHISPER_SAMPLE_RATE / sample_rate)
                )
            
            # Normalize if requested
            if normalize:
                logger.debug("Normalizing audio")
                audio = audio / np.max(np.abs(audio))
            
            return audio, AudioUtils.WHISPER_SAMPLE_RATE
            
        except Exception as e:
            logger.error(f"Failed to load audio file: {str(e)}")
            raise
    
    @staticmethod
    def get_audio_info(file_path: Union[str, Path]) -> dict:
        """Get audio file information using ffprobe
        
        Args:
            file_path: Path to audio file
            
        Returns:
            dict: Audio file information including:
                - format
                - sample_rate
                - channels
                - bit_depth
                - duration
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(file_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"FFprobe failed: {result.stderr}")
            
            import json
            info = json.loads(result.stdout)
            
            # Extract relevant information
            audio_stream = next(s for s in info['streams'] if s['codec_type'] == 'audio')
            
            return {
                'format': info['format']['format_name'],
                'sample_rate': int(audio_stream['sample_rate']),
                'channels': int(audio_stream['channels']),
                'bit_depth': int(audio_stream.get('bits_per_sample', 0)),
                'duration': float(info['format']['duration'])
            }
            
        except Exception as e:
            logger.error(f"Failed to get audio info: {str(e)}")
            raise 