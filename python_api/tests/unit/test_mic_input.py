import os
import pytest
import numpy as np
import logging
from python_api.src.input.mic_input import MicrophoneInput
import time
from pathlib import Path

def setup_module(module):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def test_microphone_record_and_save(tmp_path):
    logger = logging.getLogger("test_microphone_record_and_save")
    logger.info("Checking microphone availability...")
    # 检查麦克风可用性
    try:
        mic = MicrophoneInput(duration=60)
        logger.info("MicrophoneInput initialized successfully.")
    except RuntimeError as e:
        logger.warning(f"No microphone available: {e}")
        pytest.skip(f"No microphone available: {e}")
        return

    # 保存到本地文件
    output_dir = "sample/audio"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "test_output.wav")
    logger.info(f"Recording and saving audio to file: {output_file}")
    try:
        audio_data = mic.record_and_save(str(output_file))
        logger.info("Audio recorded and saved successfully.")
    except Exception as e:
        logger.error(f"Failed to record and save audio: {e}")
        raise

    # 检查文件是否存在且非空
    output_path = Path(output_file)
    assert output_path.exists(), "Output file was not created."
    assert output_path.stat().st_size > 0, "Output file is empty."

    # 检查audio_data返回内容
    assert isinstance(audio_data, np.ndarray), "Audio data is not a numpy array."
    assert audio_data.size > 0, "Audio data is empty."
    logger.info("Test completed successfully.")
