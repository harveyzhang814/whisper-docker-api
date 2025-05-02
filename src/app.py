from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import whisper
import torch
import numpy as np
import tempfile
import os
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')  # Try to load .env.local first
load_dotenv('.env')  # Fall back to .env if exists

# Configure logging
logger.add("whisper.log", rotation="500 MB")

app = FastAPI(title="Whisper Transcription API")

# Load Whisper model
MODEL_NAME = os.getenv("WHISPER_MODEL", "base")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "16"))

logger.info(f"Loading Whisper model: {MODEL_NAME}")
model = whisper.load_model(MODEL_NAME)
model.eval()

class TranscriptionResponse(BaseModel):
    text: str
    segments: List[dict]

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Whisper Transcription API")
    # Verify CUDA availability
    if torch.cuda.is_available():
        logger.info(f"CUDA available: {torch.cuda.get_device_name(0)}")
    else:
        logger.warning("CUDA not available, using CPU")

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile,
    stream: bool = False,
    background_tasks: BackgroundTasks = None
):
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio.filename).suffix) as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_file.flush()

            # Transcribe audio
            result = model.transcribe(
                temp_file.name,
                fp16=torch.cuda.is_available()
            )

            # Clean up temp file
            background_tasks.add_task(os.unlink, temp_file.name)

            return TranscriptionResponse(
                text=result["text"],
                segments=[{
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"]
                } for seg in result["segments"]]
            )

    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe/stream")
async def transcribe_stream(audio: UploadFile):
    async def generate_transcription():
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio.filename).suffix) as temp_file:
                content = await audio.read()
                temp_file.write(content)
                temp_file.flush()

                # Process audio and stream segments
                result = model.transcribe(
                    temp_file.name,
                    fp16=torch.cuda.is_available()
                )
                
                # Stream each segment as it's processed
                for segment in result["segments"]:
                    yield f"data: {segment['text']}\n\n"

                # Clean up
                os.unlink(temp_file.name)

        except Exception as e:
            logger.error(f"Error during streaming transcription: {str(e)}")
            yield f"error: {str(e)}\n\n"

    return StreamingResponse(
        generate_transcription(),
        media_type="text/event-stream"
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": MODEL_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000) 