from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.logging_config import get_logger

logger = get_logger(__name__)
app = FastAPI(title="Digital Castle API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "🏰 Digital Castle Running"}

@app.get("/api/status")
async def status():
    return {"status": "online", "version": "2.0.0"}

@app.get("/api/agents")
async def agents():
    return {"agents": ["Market Scout", "Developer", "DevSecOps"], "count": 22}

@app.get("/api/tasks")
async def get_tasks():
    return {"tasks": []}

@app.post("/api/tasks")
async def create_task(title: str, description: str, agent: str):
    return {"task_id": 1, "status": "created"}

@app.get("/api/analytics")
async def analytics():
    return {"total": 0, "completed": 0}
