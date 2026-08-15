from fastapi import FastAPI

app = FastAPI(title="Digital Castle")

@app.get("/")
def root():
    return {"message": "🏰 Digital Castle Online"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/status")
def status():
    return {"status": "online", "agents": 22}

@app.get("/api/agents")
def agents():
    return {"agents": ["Dev", "DevOps", "QA"], "count": 22}
