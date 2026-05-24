from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat, general, translation, telecom, voice
from app.api.routes import voice_rest, documents
from app.config import settings

app = FastAPI(title=settings.APP_NAME)

# CORS for frontend - use env var for production
allowed_origins = settings.CORS_ORIGINS.split(",") if hasattr(settings, 'CORS_ORIGINS') and settings.CORS_ORIGINS else ["http://localhost:5173", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(general.router, prefix="/api", tags=["general"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(translation.router, prefix="/api", tags=["translation"])
app.include_router(telecom.router, prefix="/api", tags=["telecom"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(voice.router, prefix="/api", tags=["voice-ws"])
app.include_router(voice_rest.router, prefix="/api", tags=["voice-rest"])

@app.get("/")
def root():
    return {
        "message": "Universal Translation API is running",
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "services": {
            "chat": "/api/chat",
            "translation": "/api/translate",
            "documents": "/api/documents",
            "voice_websocket": "/api/ws/translate",
            "transcribe_websocket": "/api/ws/transcribe",
            "voice_transcribe": "/api/voice/transcribe",
            "voice_synthesize": "/api/voice/synthesize",
            "voice_capabilities": "/api/voice/capabilities"
        },
        "supported_languages": settings.SUPPORTED_LANGUAGES
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
