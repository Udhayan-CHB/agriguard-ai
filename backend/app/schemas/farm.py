from pydantic import BaseModel
from typing import Optional

class FarmProfileCreate(BaseModel):
    username: str
    location: str
    crop: str
    farm_size_hectares: float
    problem: Optional[str] = None

class FarmProfileRead(BaseModel):
    id: int
    user_id: int
    location: str
    crop: str
    farm_size_hectares: float
    problem: Optional[str] = None

    class Config:
        form_attributes = True