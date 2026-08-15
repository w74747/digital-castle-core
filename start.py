from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import uvicorn
import os
from app.database import init_db
from app.routes import router as basic_router

app = FastAPI(title="Digital Castle API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    try:
        init_db()
    except:
        pass

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/")
def root():
    return {"message": "🏰 Digital Castle v3.0"}

@app.get("/api/status")
def api_status():
    return {"status": "online", "version": "3.0.0", "agents": 22}

@app.get("/api/agents")
def api_agents():
    agents = ["Market Scout", "Developer", "DevSecOps", "QA Engineer", "Tech Writer",
              "Database Admin", "SEO Specialist", "CMO", "Content Writer", "Media Producer",
              "Social Manager", "Brand Guardian", "CFO", "API Sentinel", "Cost Auditor",
              "Investment Advisor", "Performance Coach", "Project Manager", "Architect",
              "UI/UX Designer", "Business Consultant", "Backup Manager"]
    return {"agents": agents, "count": len(agents)}

# Mock data
tasks_db = []
users_db = {}

@app.post("/api/register")
def register(username: str, email: str, password: str):
    if username in users_db:
        return {"error": "User exists"}, 400
    users_db[username] = {"email": email, "password": password}
    return {"id": 1, "username": username}

@app.post("/api/login")
def login(username: str, password: str):
    if username not in users_db or users_db[username]["password"] != password:
        return {"error": "Invalid"}, 401
    from app.auth import create_access_token
    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/tasks")
def get_tasks():
    return {"tasks": tasks_db}

@app.post("/api/tasks")
def create_task(title: str, agent: str = "Developer"):
    task = {"id": len(tasks_db) + 1, "title": title, "agent": agent, "status": "pending"}
    tasks_db.append(task)
    return {"id": task["id"]}

@app.post("/api/v2/tasks/advanced")
def create_task_advanced(title: str, agent: str, description: str = ""):
    task = {"id": len(tasks_db) + 1, "title": title, "agent": agent, "status": "pending", "description": description}
    tasks_db.append(task)
    return {"id": task["id"], "status": "created"}

@app.get("/api/analytics")
def analytics():
    completed = len([t for t in tasks_db if t["status"] == "completed"])
    return {"total": len(tasks_db), "completed": completed}

@app.get("/api/v2/analytics/advanced")
def analytics_advanced():
    by_agent = {}
    for task in tasks_db:
        agent = task.get("agent", "Unknown")
        if agent not in by_agent:
            by_agent[agent] = {"total": 0, "completed": 0}
        by_agent[agent]["total"] += 1
        if task.get("status") == "completed":
            by_agent[agent]["completed"] += 1
    
    total = len(tasks_db)
    completed = len([t for t in tasks_db if t["status"] == "completed"])
    return {
        "summary": {"total": total, "completed": completed},
        "by_agent": by_agent
    }

app.include_router(basic_router)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(title="Digital Castle API", version="3.0.0", routes=app.routes)
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
