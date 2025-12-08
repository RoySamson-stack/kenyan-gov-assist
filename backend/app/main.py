from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat, health, translation, telecom
from app.config import settings

app = FastAPI(title=settings.APP_NAME)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(translation.router, prefix="/api", tags=["translation"])
app.include_router(telecom.router, prefix="/api", tags=["telecom"])

@app.get("/")
def root():
    return {"message": "Serikali Yangu API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
