from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Digital Castle API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
tasks_db = []
task_id_counter = 1

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "🏰 Digital Castle Running"}

@app.get("/api/status")
async def status():
    return {"status": "online", "version": "2.0.0", "agents": 22}

@app.get("/api/agents")
async def agents():
    return {"agents": ["Market Scout", "Developer", "DevSecOps", "DevSecOps", "QA Engineer", "Tech Writer", "Database Admin", "SEO Specialist", "CMO", "Content Writer", "Media Producer", "Social Manager", "Brand Guardian", "CFO", "API Sentinel", "Cost Auditor", "Investment Advisor", "Performance Coach", "Project Manager", "Architect", "UI/UX Designer", "Business Consultant"], "count": 22}

@app.get("/api/tasks")
async def get_tasks():
    return {"tasks": tasks_db, "count": len(tasks_db)}

@app.post("/api/tasks")
async def create_task(title: str, description: str = "", agent: str = "Developer"):
    global task_id_counter
    task = {"id": task_id_counter, "title": title, "description": description, "agent": agent, "status": "pending"}
    tasks_db.append(task)
    task_id_counter += 1
    return {"task_id": task["id"], "status": "created"}

@app.get("/api/analytics")
async def analytics():
    completed = len([t for t in tasks_db if t["status"] == "completed"])
    return {"total_tasks": len(tasks_db), "completed": completed, "pending": len(tasks_db) - completed}
