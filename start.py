from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

app = FastAPI(title="Digital Castle", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
tasks = []
users = {}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/")
def root():
    return {"message": "🏰 Digital Castle v3.0 Online"}

@app.get("/api/status")
def status():
    return {"status": "online", "version": "3.0.0", "agents": 22}

@app.get("/api/agents")
def agents():
    return {"agents": ["Developer", "DevSecOps", "QA"], "count": 22}

@app.get("/api/tasks")
def get_tasks():
    return {"tasks": tasks}

@app.post("/api/tasks")
def create_task(title: str):
    task = {"id": len(tasks)+1, "title": title}
    tasks.append(task)
    return task

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
