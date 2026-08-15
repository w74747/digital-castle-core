from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tasks = []

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "🏰 Digital Castle Running"}

@app.get("/api/status")
def status():
    return {"status": "online", "version": "2.0.0"}

@app.get("/api/agents")
def agents():
    return {"agents": ["Developer", "DevSecOps", "QA"], "count": 22}

@app.get("/api/tasks")
def get_tasks():
    return {"tasks": tasks}

@app.post("/api/tasks")
def create_task(title: str, agent: str = "Developer"):
    task = {"id": len(tasks) + 1, "title": title, "agent": agent, "status": "pending"}
    tasks.append(task)
    return {"task_id": task["id"]}

@app.get("/api/analytics")
def analytics():
    return {"total": len(tasks), "completed": 0}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
