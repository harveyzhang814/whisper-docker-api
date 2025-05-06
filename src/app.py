from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, UploadFile, File
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
    audio_file: UploadFile = File(...),
    language: Optional[str] = None,
    api_key: str = Depends(api_key_header)
):
    await verify_api_key(api_key)
    
    try:
        # Read audio file
        audio_data, sample_rate = sf.read(audio_file.file)
        
        # Use StandardAPI for transcription
        api = StandardAPI()
        result = api.transcribe(audio_data, language=language)
        
        return TranscriptionResponse(
            text=result,
            segments=[]  # TODO: Implement segment handling
        )
        
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe/stream")
async def transcribe_stream(
    audio_file: UploadFile = File(...),
    language: Optional[str] = None,
    api_key: str = Depends(api_key_header)
):
    await verify_api_key(api_key)
    
    async def generate_transcription():
        try:
            # Read audio file
            audio_data, sample_rate = sf.read(audio_file.file)
            
            # Use StreamingAPI for transcription
            api = StreamingAPI()
            for segment in api.transcribe_stream(audio_data, language=language):
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