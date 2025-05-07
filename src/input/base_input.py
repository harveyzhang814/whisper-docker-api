from abc import ABC, abstractmethod
import numpy as np
import sounddevice as sd
from typing import List, Tuple, Optional

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

    @staticmethod
    def list_microphones() -> List[Tuple[int, str]]:
        """List all available microphone devices
        
        Returns:
            List[Tuple[int, str]]: List of tuples containing device index and name
        """
        devices = []
        try:
            # Get all audio devices
            device_list = sd.query_devices()
            
            # Filter input devices (microphones)
            for i, device in enumerate(device_list):
                if device['max_input_channels'] > 0:
                    devices.append((i, device['name']))
        except Exception as e:
            print(f"Error listing microphones: {str(e)}")
        
        return devices
    
    @staticmethod
    def get_default_microphone() -> Optional[int]:
        """Get the default microphone device index
        
        Returns:
            Optional[int]: Default microphone device index or None if not available
        """
        try:
            device = sd.query_devices(kind='input')
            return device.get('index')
        except Exception as e:
            print(f"Error getting default microphone: {str(e)}")
            return None
    
    @staticmethod
    def is_microphone_available(device_index: Optional[int] = None) -> bool:
        """Check if a specific microphone or any microphone is available
        
        Args:
            device_index: Specific device index to check, or None to check any microphone
        
        Returns:
            bool: True if microphone is available, False otherwise
        """
        try:
            if device_index is not None:
                # Check specific device
                device = sd.query_devices(device_index)
                return device['max_input_channels'] > 0
            else:
                # Check if any input device is available
                return len(BaseInput.list_microphones()) > 0
        except Exception as e:
            print(f"Error checking microphone availability: {str(e)}")
            return False 