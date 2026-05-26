from fastapi import FastAPI
from app.config import settings
app=FastAPI(title=settings.APP_NAME)

#home route
@app.get("/")
def root():
    return{
        "message":"Knowledge agent running",
        "environment":settings.APP_ENV
    }

#health route 
@app.get("/health")
def health_check():
    return{
        "status":"healthy"
    }
    