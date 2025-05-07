import numpy as np
import sounddevice as sd
import time
from typing import Optional
from .base_input import BaseInput
import threading
from src.utils.hotkey_listener import HotkeyListener

class MicrophoneInput(BaseInput):
    """Class for handling complete microphone recording"""
    
    def __init__(self, device: Optional[int] = None, duration: Optional[float] = None):
        """Initialize microphone input for complete recording
        
        Args:
            device: Audio device index
            duration: Recording duration in seconds (None for manual stop)
            
        Raises:
            RuntimeError: If no microphone is available or specified device is not available
        """
        super().__init__()
        
        # Check microphone availability
        if not self.is_microphone_available(device):
            if device is not None:
                raise RuntimeError(f"Microphone device {device} is not available")
            else:
                raise RuntimeError("No microphone is available")
        
        self.device = device if device is not None else self.get_default_microphone()
        self.duration = duration
        self._running_event = threading.Event()
        self._stream = None
        self._audio_buffer = []
        self._start_time = None
        self._should_stop = False
        self._hotkey_listener = None
        self._hotkey_thread = None
        self._hotkey_triggered = False
    
    def get_audio(self) -> np.ndarray:
        """Get complete recorded audio data
        
        Returns:
            numpy.ndarray: Complete audio recording as a numpy array
        """
        print("get_audio() called, buffer length:", len(self._audio_buffer))
        if not self._audio_buffer:
            print("get_audio() returning empty array")
            return np.array([])
        result = np.concatenate(self._audio_buffer)
        print("get_audio() returning array of shape:", result.shape)
        return result
    
    def _audio_callback(self, indata: np.ndarray, frames: int, 
                       time_info: dict, status: sd.CallbackFlags) -> None:
        """Internal callback for audio recording"""
        print("audio_callback called")  # 调试输出
        if status:
            print(f"Status: {status}")
        self._audio_buffer.append(indata.copy())
        
        # Stop recording if duration is reached
        if self.duration is not None and self._start_time is not None:
            elapsed = time.time() - self._start_time
            print(f"Elapsed time: {elapsed:.2f}s / {self.duration}s")
            if elapsed >= self.duration:
                print("Duration reached, should stop set to True...")
                self._should_stop = True
    
    def _hotkey_callback(self):
        if not self._hotkey_triggered:
            self._hotkey_triggered = True
            self._should_stop = True

    def _start_hotkey_listener(self):
        self._hotkey_listener = HotkeyListener()
        self._hotkey_listener.set_callback(self._hotkey_callback)
        self._hotkey_listener.start()

    def _stop_hotkey_listener(self):
        if self._hotkey_listener:
            self._hotkey_listener.stop()
            self._hotkey_listener = None
        self._hotkey_triggered = False

    def start(self) -> None:
        """Start recording from microphone"""
        if not self._running_event.is_set():
            self._audio_buffer = []
            self._should_stop = False
            self._start_hotkey_listener()
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=self._audio_callback,
                device=self.device
            )
            self._start_time = time.time()
            self._stream.start()
            print("InputStream started")  # 调试输出
            self._running_event.set()
    
    def stop(self) -> None:
        """Stop recording from microphone"""
        try:
            print(f"stop() called, self._running={self._running_event.is_set()}")
            if self._running_event.is_set():
                print("Stopping recording...")
                if self._stream is not None:
                    self._stream.stop()
                    self._stream.close()
                self._stream = None
                print("Recording stopped successfully")
        except Exception as e:
            print(f"Error stopping recording: {e}")
            self._stream = None
        finally:
            self._stop_hotkey_listener()
            self._running_event.clear()
            print("self._running_event cleared in stop()")
    
    @property
    def is_running(self) -> bool:
        """Check if recording is active"""
        return self._running_event.is_set()
    
    @property
    def should_stop(self) -> bool:
        return self._should_stop
    
    def save_to_file(self, filename: str) -> None:
        """Save recorded audio to a file
        
        Args:
            filename: Path to save the audio file
        """
        audio_data = self.get_audio()
        if len(audio_data) > 0:
            import soundfile as sf
            sf.write(filename, audio_data, self.sample_rate)

    def record_and_save(self, filename: str) -> np.ndarray:
        """Record audio (blocking), save to file, and return the numpy array.
        Args:
            filename: Path to save the audio file
        Returns:
            numpy.ndarray: Complete audio recording as a numpy array
        """
        self.start()
        while self.is_running:
            if self.should_stop:
                self.stop()
            time.sleep(0.05)
        self.save_to_file(filename)
        return self.get_audio() 