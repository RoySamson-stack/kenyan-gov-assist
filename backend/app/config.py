from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Serikali Yangu"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    # Use the 8B variant by default so it fits 12‑16 GB RAM VPS tiers
    OLLAMA_MODEL: str = "llama3.1:8b"
    VECTOR_DB_PATH: str = "../data/vector_db/chroma"
    RAW_DOCS_PATH: str = "../data/raw"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    class Config:
        env_file = ".env"

settings = Settings()
