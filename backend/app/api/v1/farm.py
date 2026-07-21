from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import User, FarmProfile
from app.schemas.farm import FarmProfileCreate, FarmProfileRead
from app.api.deps import get_current_user, get_db

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=FarmProfileRead)
def create_farm_profile(profile: FarmProfileCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Create or get user
    user = db.query(User).filter(User.username == profile.username).first()
    if not user:
        user = User(username=profile.username)
        db.add(user)
        db.commit()
        db.refresh(user)

    farm = db.query(FarmProfile).filter(
        FarmProfile.user_id == current_user.id,
        FarmProfile.location.ilike(profile.location),
        FarmProfile.crop.ilike(profile.crop),
    ).first()
    if farm:
        farm.farm_size_hectares = profile.farm_size_hectares
        farm.problem = profile.problem
    else:
        farm = FarmProfile(
            user_id=current_user.id,
            location=profile.location,
            crop=profile.crop,
            farm_size_hectares=profile.farm_size_hectares,
            problem=profile.problem,
        )
        db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


@router.get("/", response_model=list[FarmProfileRead])
def list_farm_profiles(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username.strip()).first()
    if not user:
        return []
    return db.query(FarmProfile).filter(FarmProfile.user_id == user.id).order_by(FarmProfile.created_at.desc()).all()
