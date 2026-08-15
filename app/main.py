from fastapi import FastAPI
from app.logging_config import get_logger

logger = get_logger(__name__)
app = FastAPI(title="Digital Castle API")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "digital-castle"}

@app.get("/")
async def root():
    return {"message": "🏰 Digital Castle S.P.C - Running"}

from app.api import router
app.include_router(router)
