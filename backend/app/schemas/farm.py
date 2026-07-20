from pydantic import BaseModel, Field, field_validator
from typing import Optional

class FarmProfileCreate(BaseModel):
    username: str = Field(min_length=2, max_length=80)
    location: str = Field(min_length=2, max_length=120)
    crop: str = Field(min_length=2, max_length=60)
    farm_size_hectares: float = Field(gt=0, le=100000)
    problem: Optional[str] = None

    @field_validator("username", "location", "crop")
    @classmethod
    def non_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty")
        return value

    @field_validator("problem")
    @classmethod
    def clean_problem(cls, value: Optional[str]) -> Optional[str]:
        return value.strip() if value and value.strip() else None

class FarmProfileRead(BaseModel):
    id: int
    user_id: int
    location: str
    crop: str
    farm_size_hectares: float
    problem: Optional[str] = None

    class Config:
        form_attributes = True
