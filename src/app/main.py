from fastapi import FastAPI
import logging

# Basic logging config
logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("app")

app = FastAPI(title="Call Transcriber Service", version="0.1.0")


@app.get("/health")
def health():
    """
    Basic readiness / liveness probe.
    """
    logger.info("Health check requested")
    return {"status": "ok"}