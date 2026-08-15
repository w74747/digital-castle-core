from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import uvicorn
from app.database import init_db
from app.routes import router

app = FastAPI(
    title="Digital Castle API",
    description="Enterprise AI Agent System",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "🏰 Digital Castle Running"}

@app.get("/api/status")
def api_status():
    return {"status": "online", "version": "2.0.0", "agents": 22}

@app.get("/api/agents")
def api_agents():
    agents = ["Market Scout", "Developer", "DevSecOps", "QA Engineer", "Tech Writer", 
              "Database Admin", "SEO Specialist", "CMO", "Content Writer", "Media Producer",
              "Social Manager", "Brand Guardian", "CFO", "API Sentinel", "Cost Auditor",
              "Investment Advisor", "Performance Coach", "Project Manager", "Architect",
              "UI/UX Designer", "Business Consultant", "Backup Manager"]
    return {"agents": agents, "count": len(agents)}

app.include_router(router)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Digital Castle API",
        version="2.0.0",
        description="Enterprise AI Agent System",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
