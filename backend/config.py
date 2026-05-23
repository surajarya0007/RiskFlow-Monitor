import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    PORT: int = int(os.getenv("BACKEND_PORT", 8000))
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/governanceops",
    )
    WS_PATH: str = os.getenv("WS_PATH", "/ws/stream")
    COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")
    COINGECKO_BASE_URL: str = os.getenv(
        "COINGECKO_BASE_URL",
        "https://api.coingecko.com/api/v3/simple/price",
    )

settings = Settings()
