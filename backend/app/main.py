from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.documents.routes import router as documents_router

# Import models so SQLAlchemy detects them
from app import models  # noqa: F401


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)


@app.get("/")
def root():
    return {
        "message": "AI Document Intelligence Agent backend is running",
        "environment": settings.APP_ENV
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/db/ping")
def db_ping(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1")).scalar()

    return {
        "database": "connected",
        "result": result
    }


app.include_router(documents_router)