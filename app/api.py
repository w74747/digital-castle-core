from fastapi import APIRouter, HTTPException
from app.smart_llm_router import smart_router
from app.prime_agent_adapter import prime_agent_system

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/agents")
async def list_agents():
    agents = list(prime_agent_system.pool.agents.keys())
    return {"agents": agents, "count": len(agents)}

@router.post("/ask")
async def ask(prompt: str):
    result = await smart_router.route(prompt, task_type="coding")
    return {"response": result}

@router.get("/status")
async def status():
    return {
        "status": "online",
        "agents": len(prime_agent_system.pool.agents),
        "version": "1.5.0"
    }
