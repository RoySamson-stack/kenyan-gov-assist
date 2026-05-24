from fastapi import APIRouter

router = APIRouter()

@router.get("/general")
def general_check():
    return {
        "status": "generaly",
        "service": "Universal Translation API"
    }
