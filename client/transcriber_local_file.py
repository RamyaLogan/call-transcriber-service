import sys
from pathlib import Path

import requests

DEFAULT_API_URL = "http://localhost:8000/transcribe"
DEFAULT_AUDIO_PATH = Path("sample_audio/hello.m4a")


def main():
    """
    Minimal usage example:
    - Sends a local audio file to the transcription service
    - Prints the transcript text and full JSON response
    """
    # Usage:
    #   python client/transcriber_local_file.py
    #   python client/transcriber_local_file.py path/to/audio.m4a
    #   python client/transcriber_local_file.py path/to/audio.m4a http://server:8000/transcribe

    audio_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_AUDIO_PATH
    api_url = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_API_URL

    if not audio_path.exists():
        print(f"Error: audio file not found: {audio_path}")
        sys.exit(1)

    print(f"Sending {audio_path} to {api_url}...")

    with audio_path.open("rb") as f:
        files = {"file": (audio_path.name, f, "audio/mp4")}

        resp = requests.post(api_url, files=files)

    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        print(f"Request failed: {e}")
        print("Response:", resp.text)
        sys.exit(1)

    data = resp.json()
    print("\n=== Transcription Result ===")
    print(data.get("text", ""))

    print("\n--- Full Response JSON ---")
    print(data)


if __name__ == "__main__":
    main()