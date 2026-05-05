from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat, health, translation, telecom, voice
from app.api.routes import voice_rest
from app.config import settings

app = FastAPI(title=settings.APP_NAME)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite dev server + Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(translation.router, prefix="/api", tags=["translation"])
app.include_router(telecom.router, prefix="/api", tags=["telecom"])
app.include_router(voice.router, prefix="/api", tags=["voice-ws"])
app.include_router(voice_rest.router, prefix="/api", tags=["voice-rest"])

@app.get("/")
def root():
    return {
        "message": "Serikali Yangu API is running",
        "app_name": settings.APP_NAME,
        "services": {
            "chat": "/api/chat",
            "translation": "/api/translate",
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
