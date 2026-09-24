from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import create_tables
from app.routes.screen import router as screen_router


app = FastAPI(
    title="DAKSH API",
    description="Document Authentication & Knowledge-based Screening Hub",
    version="1.0.0"
)


# Create database tables
create_tables()


# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Connect document screening routes
app.include_router(screen_router)


@app.get("/")
def home():
    return {
        "message": "DAKSH Backend is Running"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "project": "DAKSH"
    }