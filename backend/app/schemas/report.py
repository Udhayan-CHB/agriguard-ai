from pydantic import BaseModel
from typing import Optional

class ReportRequest(BaseModel):
    farm_profile_id: int

class ReportResponse(BaseModel):
    weather: Optional[str] = None
    diseases: Optional[str] = None
    market: Optional[str] = None
    sustainability: Optional[str] = None
    final_recommendation: str