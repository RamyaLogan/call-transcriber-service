import logging
import os
import tempfile
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException, status

from .config import settings
from .speech_to_text import transcribe_audio
from .models import TranscriptionResponse, ErrorResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("app")

app = FastAPI(title="Call Transcriber Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for this exercise; in production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Serve client (HTML/JS) from /client
app.mount(
    "/client",
    StaticFiles(directory="client", html=True),
    name="client"
)
# Supported audio types
ALLOWED_CONTENT_TYPES: List[str] = [
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/x-m4a",
    "audio/aac",
    "audio/ogg",
    "audio/webm",
    "application/octet-stream",
]

@app.get("/health")
def health():
    logger.info("Health check requested")
    return {"status": "ok"}


@app.post(
    "/transcribe",
    response_model=TranscriptionResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def transcribe(file: UploadFile = File(...)):
    """
    Accepts an audio file and returns a transcription text.

    Expects multipart/form-data with `file`.
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        logger.warning("Unsupported content type: %s", file.content_type)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported content type: {file.content_type}",
        )

    data = await file.read()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large (>{settings.max_file_size_mb} MB)",
        )

    temp_file_path = None

    try:
        # Save to a temporary file so faster-whisper can read it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
            tmp.write(data)
            temp_file_path = tmp.name

        result = transcribe_audio(temp_file_path)
        return TranscriptionResponse(**result)

    except HTTPException:
        # Re-raise explicit HTTP errors
        raise
    except Exception as exc:
        logger.exception("Error during transcription: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transcribe audio",
        )
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError:
                logger.warning("Failed to remove temp file: %s", temp_file_path)