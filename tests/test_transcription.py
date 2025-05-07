import os
import subprocess
from src.input.file_input import FileInput
from src.output.text_output import TextOutput
import requests
from loguru import logger
import soundfile as sf

def test_local_transcription():
    # Initialize components
    sample_file = os.path.join("sample", "audio", "test_file.m4a")
    file_input = FileInput(wav_file)
    text_output = TextOutput()

    try:
        # Start audio input
        file_input.start()
        
        # Get audio data
        audio_data = file_input.get_audio()
        
        # Prepare the file for upload
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            # Save original audio to temporary file
            sf.write(temp_file.name, audio_data, 16000)  # Using standard sample rate
            temp_path = temp_file.name
            
            # Call API for transcription
            with open(temp_path, 'rb') as audio_file:
                files = {
                    'audio': ('audio.wav', audio_file, 'audio/wav')
                }
                
                # Add parameters
                data = {
                    'model': 'base',
                    'batch_size': 16
                }
                
                # Send request
                response = requests.post(
                    "http://localhost:8090/transcribe",
                    files=files,
                    data=data
                )
                response.raise_for_status()
                
                # Parse response
                result = response.json()
                transcription = result.get("text", "")
        
        # Format the output
        text_output.configure(
            capitalize_sentences=True,
            add_punctuation=True,
            remove_extra_spaces=True
        )
        formatted_text = text_output.format(transcription)
        
        # Print results
        print("\nTranscription Results:")
        print("---------------------")
        print(f"Original text: {transcription}")
        print(f"Formatted text: {formatted_text}")
        
        # Basic assertions
        assert isinstance(transcription, str)
        assert len(transcription) > 0
        assert isinstance(formatted_text, str)
        assert len(formatted_text) > 0
        
        return formatted_text
        
    finally:
        # Cleanup
        file_input.stop()
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {e}")
        try:
            os.unlink(wav_file)  # Remove the converted wav file
        except Exception as e:
            logger.warning(f"Failed to delete wav file: {e}")

if __name__ == "__main__":
    # Run the test
    result = test_local_transcription() 