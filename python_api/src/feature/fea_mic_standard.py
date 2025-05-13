import os
from python_api.src.input.mic_input import MicrophoneInput
from python_api.src.api.standard_api import StandardAPI
from python_api.src.output.text_output import TextOutput
from python_api.src.output.json_output import JSONOutput  # 如有实现可解开
# from python_api.src.output.srt_output import SrtOutput    # 如有实现可解开
from python_api.src.utils.hotkey_listener import HotkeyListener

class MicStandardTranscrible:
    OUTPUT_CLASS_MAP = {
        "text": TextOutput,
        "json": JSONOutput,   # 如有实现可解开
        # "srt": SrtOutput,     # 如有实现可解开
    }

    def __init__(self, api_key=None, base_url=None, duration=5, output_file="sample/audio/feature_mic_to_text.wav", output_format="text"):
        self.api_key = api_key or os.getenv("API_KEY")
        self.base_url = base_url or os.getenv("API_BASE_URL")
        self.duration = duration
        self.output_file = output_file
        self.output_format = output_format
        self.mic = None

    def run(self):
        # 1. 录音并保存
        self.mic = MicrophoneInput(duration=self.duration)
        print(f"[MicStandardTranscrible] Start recording... (press ctrl+r to stop early)")
        audio_data = self.mic.record_and_save(self.output_file)
        print(f"[MicStandardTranscrible] Audio saved to {self.output_file}, shape: {audio_data.shape}")

        # 2. 调用API转录
        api = StandardAPI(api_key=self.api_key, base_url=self.base_url)
        print("[MicStandardTranscrible] Transcribing audio via StandardAPI...")
        transcribed_text = api.transcribe(audio_data)
        print("[MicStandardTranscrible] Transcription result:", transcribed_text)

        # 3. 格式化输出
        output_cls = self.OUTPUT_CLASS_MAP.get(self.output_format, TextOutput)
        formatter = output_cls()
        if hasattr(formatter, 'format'):
            formatted_text = formatter.format(transcribed_text)
        else:
            formatted_text = str(transcribed_text)
        print(f"[MicStandardTranscrible] Formatted text ({self.output_format}):", formatted_text)
        return formatted_text

class MicStandardAppHotKey:
    """
    热键触发的麦克风录音转写应用。
    支持自定义热键、录音参数、输出格式，适合独立运行或集成到其他系统。
    
    用法示例：
        app = MicStandardAppHotKey(duration=60, output_format="json", hotkey=("ctrl", "t"))
        app.start()
    """
    def __init__(self, duration=5, output_file="sample/audio/feature_mic_to_text.wav", output_format="text", hotkey=("ctrl", "t"), api_key=None, base_url=None):
        """
        初始化热键录音应用。
        :param duration: 录音时长（秒）
        :param output_file: 录音文件保存路径
        :param output_format: 输出格式（如"text"、"json"）
        :param hotkey: 触发录音的组合键元组（如("ctrl", "t")）
        :param api_key: 可选，API密钥
        :param base_url: 可选，API基础URL
        """
        self.duration = duration
        self.output_file = output_file
        self.output_format = output_format
        self.hotkey = hotkey
        self.api_key = api_key
        self.base_url = base_url
        self.listener = None

    def on_hotkey(self):
        """
        热键触发时的回调。启动录音、转写并输出结果，最后自动退出程序。
        """
        feature = MicStandardTranscrible(
            api_key=self.api_key,
            base_url=self.base_url,
            duration=self.duration,
            output_file=self.output_file,
            output_format=self.output_format
        )
        print(f"[MicStandardAppHotKey] Start recording... (auto exit after recording ends)")
        formatted_text = feature.run()
        print("[MicStandardAppHotKey] Formatted text:", formatted_text)
        print("[MicStandardAppHotKey] Exiting main program.")
        import sys
        sys.exit(0)

    def start(self):
        """
        启动热键监听，等待用户按下指定组合键。
        触发后自动调用on_hotkey，完成录音和转写。
        """
        self.listener = HotkeyListener(hotkey=self.hotkey)
        self.listener.set_callback(self.on_hotkey)
        print(f"[MicStandardAppHotKey] Press {self.hotkey} to start recording. Program will exit after recording ends.")
        self.listener.start()
        if self.listener._thread:
            self.listener._thread.join()