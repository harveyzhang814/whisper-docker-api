from dotenv import load_dotenv
import os
from typing import Optional
from pathlib import Path

class Config:
    """Unified configuration management class"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from environment variables"""
        # Define config file search paths
        config_paths = [
            Path("docker_api/.env.docker.local"),
            Path("docker_api/.env.docker"),
            Path(".env.local"),
            Path(".env")
        ]
        
        # Load first available config file
        for config_path in config_paths:
            if config_path.exists():
                load_dotenv(config_path)
                break
        else:
            load_dotenv()  # Fallback to default .env
            
        # API Configuration
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8090"))
        
        # Docker API Configuration
        self.docker_api_host = os.getenv("DOCKER_API_HOST", "0.0.0.0")
        self.docker_api_port = int(os.getenv("DOCKER_API_PORT", "8091"))
        self.docker_image = os.getenv("DOCKER_IMAGE", "whisper-translation:latest")
        self.docker_container_name = os.getenv("DOCKER_CONTAINER_NAME", "whisper-translation")
        
        # Whisper Configuration
        self.whisper_model = os.getenv("WHISPER_MODEL", "base")
        self.batch_size = int(os.getenv("BATCH_SIZE", "16"))
        
        # Audio Configuration
        self.sample_rate = int(os.getenv("SAMPLE_RATE", "16000"))
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1024"))
        self.channels = int(os.getenv("CHANNELS", "1"))
        
        # Logging Configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "whisper.log")
    
    @property
    def api_base_url(self) -> str:
        """Get API base URL"""
        return f"http://{self.api_host}:{self.api_port}"
    
    @property
    def docker_api_base_url(self) -> str:
        """Get Docker API base URL"""
        return f"http://{self.docker_api_host}:{self.docker_api_port}"
    
    @classmethod
    def get_instance(cls) -> 'Config':
        """Get singleton instance"""
        return cls() 