from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Serikali Yangu"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    # Default to a CPU-friendly model so deployments don't need a GPU
    OLLAMA_MODEL: str = "llama3.2:1b"
    DEFAULT_DOMAIN: str = "civic"
    SUPPORTED_DOMAINS: List[str] = ["civic", "health"]
    SOURCE_LANGUAGE: str = "english"
    TRANSLATION_TARGET_LANGUAGES: List[str] = ["kikuyu", "luo"]
    TRANSLATION_MEMORY_PATH: str = "../data/translations"
    VECTOR_DB_PATH: str = "../data/vector_db/chroma"
    RAW_DOCS_PATH: str = "../data/raw"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    AFRICASTALKING_USERNAME: str = "sandbox"
    AFRICASTALKING_API_KEY: str = ""
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_VERIFICATION_SERVICE_SID: str = ""
    
    class Config:
        env_file = ".env"


settings = Settings()
