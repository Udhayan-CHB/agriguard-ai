from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import FarmProfile, User
from app.schemas.report import ReportRequest, ReportResponse
from app.agents.graph import agent_graph
from langchain_core.messages import HumanMessage

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ReportResponse)
def generate_report(request: ReportRequest, db: Session = Depends(get_db)):
    farm = db.query(FarmProfile).filter(FarmProfile.id == request.farm_profile_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm profile not found")

    # Force all specialist agents for a full report
    initial_state = {
        "messages": [HumanMessage(content="Generate a full report")],
        "farm_id": farm.id,
        "username": "report_user",
        "location": farm.location,
        "crop": farm.crop,
        "farm_size_hectares": farm.farm_size_hectares,
        "problem": farm.problem or "",
        "required_agents": ["weather", "crop_doctor", "market", "sustainability"],  # <-- override
    }

    result = agent_graph.invoke(initial_state)

    return ReportResponse(
        weather=result.get("weather_data", "Not available"),
        diseases=result.get("disease_data", "Not available"),
        market=result.get("market_data", "Not available"),
        sustainability=result.get("sustainability_data", "Not available"),
        final_recommendation=result.get("final_response", "Report generation failed.")
    )