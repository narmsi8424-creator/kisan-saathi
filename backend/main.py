from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(__file__))

from routers import webhook

app = FastAPI(
    title="Kisan Saathi AI",
    description="Multilingual WhatsApp AI Assistant for Indian Farmers",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router)

@app.get("/")
async def root():
    return {
        "name": "Kisan Saathi AI",
        "status": "running",
        "version": "1.0.0",
        "tagline": "Sahi Salah, Sahi Samay"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }