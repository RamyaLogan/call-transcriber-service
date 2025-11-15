import logging
import time
from pathlib import Path
from typing import Optional

from faster_whisper import WhisperModel

from .config import settings

logger = logging.getLogger(__name__)

_model: Optional[WhisperModel] = None


def get_model() -> WhisperModel:
    """
    Cache the Whisper model so it only loads once and lazily.
    """
    global _model
    if _model is None:
        logger.info(
            "Loading Whisper model '%s' (device=%s, compute_type=%s)",
            settings.model_name,
            settings.device,
            settings.compute_type,
        )
        started = time.monotonic()
        _model = WhisperModel(
            settings.model_name,
            device=settings.device,
            compute_type=settings.compute_type,
        )
        logger.info("Whisper model loaded in %.2fs", time.monotonic() - started)
    return _model


def transcribe_audio(path: str) -> dict:
    """
    Transcribes an audio file using faster-whisper.

    Returns a dict with:
      - text
      - language
      - duration_seconds
      - model
      - processing_seconds
    """
    model = get_model()
    audio_path = Path(path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    logger.info("Starting transcription for %s", audio_path)
    start = time.monotonic()

    segments, info = model.transcribe(str(audio_path))
    text = " ".join(seg.text.strip() for seg in segments).strip()

    processing_seconds = time.monotonic() - start
    logger.info(
        "Transcription finished: duration=%.2fs, processing=%.2fs, language=%s",
        info.duration,
        processing_seconds,
        info.language,
    )

    return {
        "text": text,
        "language": info.language,
        "duration_seconds": info.duration,
        "model": settings.model_name,
        "processing_seconds": processing_seconds,
    }