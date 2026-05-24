from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Universal Translation Assistant"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    # Default to a CPU-friendly model so deployments don't need a GPU
    OLLAMA_MODEL: str = "kenyan-assistant"
    # Other options: "kenyan-deepseek" (DeepSeek-based), "llama3.2:1b" (default)
    DEFAULT_DOMAIN: str = "general"
    SUPPORTED_DOMAINS: List[str] = ["general", "education", "business", "personal"]
    
    # Kenyan languages supported
    SOURCE_LANGUAGE: str = "english"
    TRANSLATION_TARGET_LANGUAGES: List[str] = [
        "swahili", "kikuyu", "luo", "kamba", "kalenjin", 
        "luhya", "somali", "kisii", "meru", "maasai"
    ]
    
    # All supported languages for voice/text
    SUPPORTED_LANGUAGES: List[str] = [
        "english", "swahili", "kikuyu", "luo", "kamba", 
        "kalenjin", "luhya", "somali", "kisii", "meru", "maasai"
    ]
    
    TRANSLATION_MEMORY_PATH: str = "../data/translations"
    VECTOR_DB_PATH: str = "../data/vector_db/chroma"
    RAW_DOCS_PATH: str = "../data/raw"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    # Speech services
    WHISPER_MODEL: str = "base"
    TTS_ENABLED: bool = True
    
    # Telecom integration
    AFRICASTALKING_USERNAME: str = "sandbox"
    AFRICASTALKING_API_KEY: str = ""
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_VERIFICATION_SERVICE_SID: str = ""
    
    # Document processing
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".xlsx", ".csv", ".txt", ".md", ".epub", ".html"]
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }


settings = Settings()
