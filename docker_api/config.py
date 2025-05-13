from dotenv import load_dotenv
import os
from typing import Optional

class Config:
    """Configuration management class"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from environment variables"""
        # 优先加载 docker_api/.env.docker.local 或 .env.docker.example
        if os.path.exists(os.path.join(os.path.dirname(__file__), ".env.docker.local")):
            load_dotenv(os.path.join(os.path.dirname(__file__), ".env.docker.local"))
        elif os.path.exists(os.path.join(os.path.dirname(__file__), ".env.docker.example")):
            load_dotenv(os.path.join(os.path.dirname(__file__), ".env.docker.example"))
        elif os.path.exists(".env.local"):
            load_dotenv(".env.local")
        else:
            load_dotenv()
            
        # API Configuration
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8090"))
        
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
    
    @classmethod
    def get_instance(cls) -> 'Config':
        """Get singleton instance"""
        return cls() 