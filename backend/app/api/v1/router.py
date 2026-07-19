from fastapi import APIRouter
from app.api.v1 import farm, chat, report

api_router = APIRouter()

api_router.include_router(farm.router, prefix="/farm", tags=["Farm Profile"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(report.router, prefix="/report", tags=["Report"])