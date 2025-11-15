from typing import Optional

from pydantic import BaseModel


class TranscriptionResponse(BaseModel):
    text: str
    language: Optional[str] = None
    duration_seconds: Optional[float] = None
    model: str
    processing_seconds: Optional[float] = None


class ErrorResponse(BaseModel):
    detail: str