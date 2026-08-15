from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.logging_config import get_logger

logger = get_logger(__name__)
app = FastAPI(title="Digital Castle API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "digital-castle"}

@app.get("/")
async def root():
    return {"message": "🏰 Digital Castle S.P.C - Running"}

@app.get("/api/status")
async def status():
    return {"status": "online", "version": "1.5.0", "agents": 22}

@app.get("/api/agents")
async def list_agents():
    try:
        from app.prime_agent_adapter import prime_agent_system
        agents = list(prime_agent_system.pool.agents.keys())
        return {"agents": agents, "count": len(agents)}
    except Exception as e:
        return {"agents": [], "count": 0, "error": str(e)}
