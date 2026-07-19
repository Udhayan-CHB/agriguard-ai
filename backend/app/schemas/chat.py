from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    username: str
    farm_profile_id: int
    message: str

class ChatResponse(BaseModel):
    reply: str
    agent_path: Optional[str] = None  # which agents were used (for later)