from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import User, FarmProfile
from app.schemas.farm import FarmProfileCreate, FarmProfileRead

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=FarmProfileRead)
def create_farm_profile(profile: FarmProfileCreate, db: Session = Depends(get_db)):
    # Create or get user
    user = db.query(User).filter(User.username == profile.username).first()
    if not user:
        user = User(username=profile.username)
        db.add(user)
        db.commit()
        db.refresh(user)

    farm = FarmProfile(
        user_id=user.id,
        location=profile.location,
        crop=profile.crop,
        farm_size_hectares=profile.farm_size_hectares,
        problem=profile.problem,
    )
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm