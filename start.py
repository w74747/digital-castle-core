from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
import sys

# القراءة من environment
PORT = int(os.getenv("PORT", "8000"))
HOST = "0.0.0.0"

# إنشاء التطبيق
app = FastAPI(title="Digital Castle", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# بيانات مؤقتة
tasks = []

@app.get("/")
def root():
    return {"message": "🏰 Digital Castle Online", "port": PORT}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/status")
def status():
    return {"status": "online", "version": "3.0", "agents": 22}

@app.get("/api/agents")
def agents():
    return {"agents": ["Dev", "DevOps", "QA"], "count": 22}

@app.get("/api/tasks")
def get_tasks():
    return {"tasks": tasks}

@app.post("/api/tasks")
def create_task(title: str):
    task = {"id": 1, "title": title}
    tasks.append(task)
    return task

if __name__ == "__main__":
    print(f"Starting on {HOST}:{PORT}")
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info"
    )
