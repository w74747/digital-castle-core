from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/")
def root():
    return {"msg": "Running"}

@app.get("/api/status")
def api_status():
    return {"status": "online"}

@app.get("/api/agents")
def api_agents():
    return {"agents": ["Dev", "QA"], "count": 22}

@app.get("/api/tasks")
def api_tasks():
    return {"tasks": []}

@app.post("/api/tasks")
def post_task(title: str):
    return {"id": 1}

@app.get("/api/analytics")
def api_analytics():
    return {"total": 0}
