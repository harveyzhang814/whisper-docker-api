import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import numpy as np
import soundfile as sf
from src.app import app

client = TestClient(app)

@pytest.fixture
def sample_audio_file():
    """Create a sample audio file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        # Generate 1 second of silence
        sample_rate = 16000
        duration = 1  # seconds
        samples = np.zeros(sample_rate * duration)
        sf.write(temp_file.name, samples, sample_rate)
        yield temp_file.name
    Path(temp_file.name).unlink()

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert "model" in response.json()

def test_transcribe_endpoint(sample_audio_file):
    """Test the transcribe endpoint with a sample audio file."""
    with open(sample_audio_file, "rb") as f:
        response = client.post(
            "/transcribe",
            files={"audio": ("test.wav", f, "audio/wav")}
        )
    assert response.status_code == 200
    result = response.json()
    assert "text" in result
    assert "segments" in result

def test_transcribe_stream_endpoint(sample_audio_file):
    """Test the streaming transcribe endpoint."""
    with open(sample_audio_file, "rb") as f:
        response = client.post(
            "/transcribe/stream",
            files={"audio": ("test.wav", f, "audio/wav")}
        )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream"

def test_invalid_audio_file():
    """Test the API with an invalid audio file."""
    with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
        temp_file.write(b"This is not an audio file")
        temp_file.seek(0)
        response = client.post(
            "/transcribe",
            files={"audio": ("test.txt", temp_file, "text/plain")}
        )
    assert response.status_code == 500 