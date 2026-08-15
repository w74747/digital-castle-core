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

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "🏰 Digital Castle Running"}

@app.get("/api/status")
async def status():
    return {"status": "online", "version": "1.5.0"}

@app.get("/api/agents")
async def agents():
    return {"agents": ["Market Scout", "Developer", "DevSecOps"], "count": 22}
