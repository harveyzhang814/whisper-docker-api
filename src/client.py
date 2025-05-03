import requests
import json
import sys
from pathlib import Path
from typing import Optional, Literal
from loguru import logger
import sseclient
from dotenv import load_dotenv
import pyperclip

# Load environment variables
load_dotenv('.env.local')  # Try to load .env.local first
load_dotenv('.env')  # Fall back to .env if exists

OutputFormat = Literal["json", "text", "clipboard"]

class WhisperClient:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip("/")
        logger.info(f"Initializing Whisper client with base URL: {self.base_url}")

    def transcribe(self, audio_path: str, stream: bool = False) -> dict:
        """
        Transcribe an audio file using the Whisper API.
        
        Args:
            audio_path: Path to the audio file
            stream: Whether to stream the results
        
        Returns:
            dict: Transcription result with text and segments
        """
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        endpoint = f"{self.base_url}/transcribe"
        if stream:
            endpoint += "/stream"

        with open(audio_path, "rb") as audio_file:
            files = {"audio": (Path(audio_path).name, audio_file, "audio/wav")}
            
            try:
                if stream:
                    response = requests.post(endpoint, files=files, stream=True)
                    client = sseclient.SSEClient(response)
                    for event in client.events():
                        if event.data.startswith("error:"):
                            raise Exception(event.data[7:])
                        print(event.data)
                    return None
                else:
                    response = requests.post(endpoint, files=files)
                    response.raise_for_status()
                    return response.json()

            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed: {str(e)}")
                raise

    def health_check(self) -> dict:
        """Check the health of the Whisper API server."""
        try:
            response = requests.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {str(e)}")
            raise

    def format_output(self, result: dict, output_format: OutputFormat = "json") -> None:
        """
        Format and output the transcription result based on the specified format.
        
        Args:
            result: The transcription result dictionary
            output_format: The desired output format ("json", "text", or "clipboard")
        
        Raises:
            pyperclip.PyperclipException: 当剪贴板操作失败时
        """
        if output_format == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # Extract plain text for both text and clipboard formats
            text = result.get("text", "").strip()
            
            if output_format == "text":
                print(text)
            elif output_format == "clipboard":
                try:
                    pyperclip.copy(text)
                except pyperclip.PyperclipException as e:
                    logger.error("剪贴板操作失败")
                    logger.error(f"错误详情: {str(e)}")
                    logger.error("可能的原因：")
                    logger.error("1. 系统剪贴板不可用")
                    logger.error("2. 没有剪贴板访问权限")
                    logger.error("3. 系统剪贴板服务未运行")
                    raise

def main():
    """Example usage of the WhisperClient."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Whisper API Client")
    parser.add_argument("audio_file", help="Path to the audio file to transcribe")
    parser.add_argument("--stream", action="store_true", help="Stream results")
    parser.add_argument("--url", default="http://localhost:5000", help="Whisper API URL")
    parser.add_argument(
        "-o", "--output-format",
        choices=["json", "text", "clipboard"],
        default="json",
        help="Output format (default: json)"
    )
    
    args = parser.parse_args()
    
    client = WhisperClient(args.url)
    
    # Check server health
    try:
        health = client.health_check()
        logger.info(f"Server health: {health}")
    except Exception as e:
        logger.error(f"Server health check failed: {e}")
        sys.exit(1)
    
    # Transcribe audio
    try:
        result = client.transcribe(args.audio_file, stream=args.stream)
        if not args.stream and result:
            client.format_output(result, args.output_format)
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 