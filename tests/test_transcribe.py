from pathlib import Path

from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)


def test_transcribe_no_file_returns_422():
    resp = client.post("/transcribe")
    assert resp.status_code == 422   # FastAPI validation error


def test_transcribe_with_sample_file():
    sample = Path("sample_audio/hello.m4a")

    if not sample.exists():
        # Don't fail CI if sample missing, just skip locally
        return

    with sample.open("rb") as f:
        files = {"file": (sample.name, f, "audio/mp4")}
        resp = client.post("/transcribe", files=files)

    assert resp.status_code == 200
    data = resp.json()

    assert "text" in data
    assert isinstance(data["text"], str)