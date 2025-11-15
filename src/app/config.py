from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_prefix="STT_",
        env_file=".env",
        case_sensitive=False,
    )

    # Whisper model settings
    model_name: str = "small"
    device: str = "cpu"
    compute_type: str = "int8"

    # Limits
    max_file_size_mb: int = 25


settings = Settings()