from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Digital Castle")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "🏰 Digital Castle - AI Agents Online"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/status")
def status():
    return {"status": "online", "agents": 22}
