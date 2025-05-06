from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.security import APIKeyHeader
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import numpy as np
import tempfile
import os
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv
import base64
import io
import soundfile as sf

from src.config import Config
from src.api.standard_api import StandardAPI
from src.api.streaming_api import StreamingAPI

# Load environment variables and configure logging
load_dotenv('.env.local')
load_dotenv('.env')
logger.add("whisper.log", rotation="500 MB")

# Initialize FastAPI app
app = FastAPI(title="Whisper Transcription API")

# Initialize API security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Load configuration
config = Config.get_instance()

class TranscriptionRequest(BaseModel):
    audio_base64: str = Field(..., description="Base64 encoded audio data")
    language: Optional[str] = Field(None, description="ISO language code")
    model: Optional[str] = Field(None, description="Whisper model name")
    batch_size: Optional[int] = Field(None, description="Batch size for processing")

    class Config:
        schema_extra = {
            "example": {
                "audio_base64": "base64_encoded_string",
                "language": "en",
                "model": "base",
                "batch_size": 16
            }
        }

class TranscriptionResponse(BaseModel):
    text: str
    segments: List[dict]

async def verify_api_key(api_key: str = None):
    if not api_key or api_key != config.api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Whisper Transcription API")
    StandardAPI()  # Initialize API with default configuration

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    request: TranscriptionRequest,
    api_key: str = Depends(api_key_header)
):
    await verify_api_key(api_key)
    
    try:
        # Decode and process audio data
        audio_bytes = base64.b64decode(request.audio_base64)
        audio_np = np.frombuffer(audio_bytes, dtype=np.float32)
        
        # Use StandardAPI for transcription
        api = StandardAPI()
        result = api.transcribe(audio_np, language=request.language)
        
        return TranscriptionResponse(
            text=result,
            segments=[]  # TODO: Implement segment handling
        )
        
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe/stream")
async def transcribe_stream(
    request: TranscriptionRequest,
    api_key: str = Depends(api_key_header)
):
    await verify_api_key(api_key)
    
    async def generate_transcription():
        try:
            # Decode and process audio data
            audio_bytes = base64.b64decode(request.audio_base64)
            audio_np = np.frombuffer(audio_bytes, dtype=np.float32)
            
            # Use StreamingAPI for transcription
            api = StreamingAPI()
            for segment in api.transcribe_stream(audio_np, language=request.language):
                yield f"data: {segment}\n\n"
                
        except Exception as e:
            logger.error(f"Error during streaming transcription: {str(e)}")
            yield f"error: {str(e)}\n\n"
            
    return StreamingResponse(
        generate_transcription(),
        media_type="text/event-stream"
    )

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model": config.whisper_model,
        "api_version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    host = config.api_host
    port = config.api_port
    uvicorn.run(app, host=host, port=port) 