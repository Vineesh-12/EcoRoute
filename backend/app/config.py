import os
from pydantic_settings import BaseSettings if False else object

class Settings:
    PROJECT_NAME: str = "Smart Waste Collection Route Optimization API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database URL: default to PostGIS if available, fallback to SQLite for local standalone run
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "mswm_routing")
    
    # If DATABASE_URL env var is provided, use it. Otherwise attempt Postgres
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    
    # Fallback SQLite path
    SQLITE_URL: str = "sqlite:///./mswm_routing.db"

settings = Settings()
