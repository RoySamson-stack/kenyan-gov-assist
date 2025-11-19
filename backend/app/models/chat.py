from pydantic import BaseModel
from typing import Optional, List

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    sources: Optional[List[str]] = []

class ChatSession(BaseModel):
    session_id: str
    messages: List[Message] = []
    language: str = "english"
