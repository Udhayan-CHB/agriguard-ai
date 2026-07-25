from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AgriGuard AI API", version="0.1.0")

# CORS – must be BEFORE the router
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def service_info():
    return {
        "service": "AgriGuard AI Backend",
        "status": "healthy",
        "health": "/health",
        "docs": "/docs",
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "AgriGuard AI Backend"}
