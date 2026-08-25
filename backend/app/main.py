import os
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base
from app.routes import auth, analyze, meals, dashboard, profile, water

# Ensure database tables are created automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NutriGuide API",
    description="AI-powered nutrition and meal analysis backend service.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure local upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Mount static folder to serve uploads
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Aggregate and prefix all routes
api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(analyze.router)
api_router.include_router(meals.router)
api_router.include_router(dashboard.router)
api_router.include_router(profile.router)
api_router.include_router(water.router)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "NutriGuide API",
        "documentation": "/docs"
    }
