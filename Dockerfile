FROM python:3.11-slim

WORKDIR /app

# System dependencies (ffmpeg for audio handling)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency definitions
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY src ./src
COPY client ./client
COPY sample_audio ./sample_audio

# Default environment variables
ENV STT_MODEL_NAME=small \
    STT_DEVICE=cpu \
    STT_COMPUTE_TYPE=int8 \
    STT_MAX_FILE_SIZE_MB=25

EXPOSE 8000

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]