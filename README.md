# Call Transcriber Service

This is a small FastAPI-based service that accepts an audio file and returns a transcript using an open-source Whisper model (via faster-whisper).  
The goal was to keep the solution simple, reliable, and easy to run locally or on a provided Ubuntu server.
---

## Overview

The service exposes two main endpoints:

- `GET /health` – readiness check  
- `POST /transcribe` – upload an audio file and receive a transcript  

Internally, it uses `faster-whisper` for CPU-optimized inference (model: `small`, compute: `int8`).  
The model is loaded lazily on first use and reused for subsequent requests.

---

## Running Locally

### 1. Install dependencies

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Start the API

```
uvicorn src.app.main:app --reload --port 8000
```

Check:

```
curl http://localhost:8000/health
```

---

## Transcribing a File (Local Example)

The repo includes a small client script to test the service:

```
python client/transcribe_local_file.py sample_audio/hello.m4a
```

Or manually using curl:

```
curl -X POST http://localhost:8000/transcribe \
  -F "file=@sample_audio/hello.m4a"
```

Example response:

```json
{
  "text": "Hello, this is a test recording...",
  "language": "en",
  "duration_seconds": 7.6,
  "model": "small",
  "processing_seconds": 1.9
}
```


## Tests

Run:

```
pytest
```

Covers:

- `/health`
- `/transcribe` error handling

---

## Docker Support

### Build image:

```
docker build -t call-transcriber-service:local .
```

### Run:

```
docker run --rm -p 8000:8000 call-transcriber-service:local
```

### Or with docker-compose:

```
docker compose up --build
```

Check:

```
curl http://localhost:8000/health
```

---

## Deployment (Ubuntu Server)

Once the deployment server IP is provided:

1. SSH into the server  
2. Clone/pull the repo  
3. Run:

```
docker compose up --build -d
```

The service will run on port `8000`.

The GitHub Actions workflow (`.github/workflows/build.yml`) currently handles build & tests, and can be extended to deploy automatically once the server IP + SSH key are available.

---

### CI/CD (GitHub Actions + Automated Deployment)

This project includes an automated deploy pipeline using GitHub Actions  
(`.github/workflows/build.yml`).

On every push to `main`, the workflow:

1. Builds & tests the application  
2. SSHes into the target Ubuntu server using the SSH key in  
   `GIT_DEPLOY_KEY` (GitHub secret)  
3. Runs the server-side deploy script:

`scripts/deploy.sh` handles:

- Installing Docker & docker-compose if missing  
- Pulling the latest code  
- Cleaning old Docker resources  
- Rebuilding & restarting the service via:

To switch servers, only update the GitHub secret `VPS_IP`.  
The pipeline will deploy to that server automatically on the next push.

## Trade-offs & Future Improvements

Given the time constraints, I prioritized:

- Reliability and simplicity  
- Clear API surface  
- Stable CPU inference  
- Dockerized deploy setup  
- Testable, modular code  

With more time, I would consider:

- Preloading the model at startup  
- Streaming transcription  
- Diarization (speaker separation)  
- Auth and rate-limiting  
- Metrics + better logging  
- GPU-accelerated model options  

---

## Notes

This solution is intentionally minimal and easy to understand. Everything is containerized and ready for deployment, with CI already in place. The design ensures that reviewers can clone, run, and validate the service quickly.

## Bonus: Mic Recording Client

As part of the bonus requirement, the project includes a lightweight browser-based client that can record audio directly from the user’s microphone and send it to the `/transcribe` endpoint.

This client is bundled inside the same FastAPI service and served from the `/client` path.  
Because everything runs under one port, there are no CORS issues or additional servers to manage.

### How to use it

1. Start the service (either locally or with Docker):

   ```
   uvicorn src.app.main:app --reload --port 8000
   ```
   or

   ```
   docker compose up --build
   ```

2. Open the mic client in your browser:

   ```
   http://localhost:8000/client
   ```

3. Click **Start Recording**, speak for a few seconds, and then click **Stop Recording**.

4. The page will send the audio to the `/transcribe` API and show the transcript on the screen.

### Testing With Live Server (Public IP - 15.223.120.41)

Once the service is deployed, you can verify it using your server’s public IP.

#### Health Check

```bash
curl http://15.223.120.41:8000/health
```

### Transcribe an Audio File

```bash
curl -X POST http://15.223.120.41:8000/transcribe \
  -F "file=@sample_audio/hello.m4a"
```

### Testing the Mic Client on Your Public Server (Optional)

By default, browsers block microphone access on:

```
http://15.223.120.41:8000
```

because it is **HTTP**, not HTTPS.

If you still want to test mic capture directly on your server’s public IP:

#### Option A — Chrome Dev Flag (Developer Mode Only)

1. Open in Chrome:
   ```
   chrome://flags/#unsafely-treat-insecure-origin-as-secure
   ```
2. Add your server origin:
   ```
   http://15.223.120.41::8000
   ```
3. Relaunch Chrome.

Now you can access:

```
http://15.223.120.41::8000/client
```

and your microphone will work.


### About the client HTML page

The browser client lives in `client/index.html` and is served by FastAPI  
under `/client`.

It uses the browser’s `MediaRecorder` API to:

1. Capture microphone audio (`audio/webm`)
2. Send it as `file` to `POST /transcribe`
3. Display the returned transcript on the page

Because it is served from the same FastAPI app, it requires **no separate server**  
and avoids any CORS issues.

Once deployed, it is available publicly at: https://ip_address:8000/client