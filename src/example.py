from input.file_input import FileInput
from input.mic_input import MicrophoneInput
from api.standard_api import StandardAPI
from api.streaming_api import StreamingAPI
from output.text_output import TextOutput
from output.json_output import JSONOutput
from config import Config

def main():
    # 加载配置
    config = Config.get_instance()
    
    # 示例1：使用文件输入和标准API
    file_input = FileInput("sample/audio/example.wav")
    standard_api = StandardAPI(api_key="your_api_key")  # 将使用配置中的 API 地址和端口
    text_output = TextOutput()
    
    # 处理文件输入
    file_input.start()
    audio_data = file_input.get_audio()
    
    # 转录和翻译
    transcription = standard_api.transcribe(audio_data, language="en")
    translation = standard_api.translate(transcription, target_language="zh")
    
    # 格式化输出
    text_output.append(translation)
    formatted_text = text_output.get_formatted_text()
    print("文件输入结果:", formatted_text)
    print(f"使用的API地址: {standard_api.base_url}")
    
    # 示例2：使用麦克风输入和流式API
    mic_input = MicrophoneInput(duration=5)  # 5秒录音
    streaming_api = StreamingAPI(api_key="your_api_key")  # 将使用配置中的 API 地址和端口
    json_output = JSONOutput()
    
    # 处理麦克风输入
    mic_input.start()
    audio_data = mic_input.get_audio()
    mic_input.stop()
    
    # 流式转录和翻译
    for partial_result in streaming_api.transcribe_stream(audio_data, language="en"):
        json_output.append(partial_result)
    
    formatted_json = json_output.get_formatted_json()
    print("麦克风输入结果:", formatted_json)
    print(f"使用的API地址: {streaming_api.base_url}")

if __name__ == "__main__":
    main() 