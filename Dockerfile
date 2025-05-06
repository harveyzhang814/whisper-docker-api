# Use Python 3.10 slim base image for ARM64
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies including ffmpeg and build tools
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    portaudio19-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY .env.example .env

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV API_PORT=8090
ENV API_HOST=0.0.0.0

# Expose port (using environment variable)
EXPOSE ${API_PORT}

# Run the application with environment variables
CMD ["sh", "-c", "uvicorn src.app:app --host ${API_HOST} --port ${API_PORT}"] 