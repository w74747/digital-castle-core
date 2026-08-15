from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
import uvicorn
from app.database import init_db
from app.routes import router
from app.advanced_routes import router as advanced_router
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Digital Castle API",
    description="Enterprise AI Agent System with Advanced Features",
    version="3.0.0"
)

# Middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Error: {exc}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})

@app.on_event("startup")
def startup():
    init_db()
    logger.info("Database initialized")

@app.get("/health")
def health():
    return {"status": "healthy", "version": "3.0.0"}

@app.get("/")
def root():
    return {"message": "🏰 Digital Castle v3.0 - Production Ready"}

@app.get("/api/status")
def api_status():
    return {"status": "online", "version": "3.0.0", "agents": 22, "features": ["WebSocket", "Email", "RateLimit", "Cache"]}

@app.get("/api/agents")
def api_agents():
    agents = ["Market Scout", "Developer", "DevSecOps", "QA Engineer", "Tech Writer", 
              "Database Admin", "SEO Specialist", "CMO", "Content Writer", "Media Producer",
              "Social Manager", "Brand Guardian", "CFO", "API Sentinel", "Cost Auditor",
              "Investment Advisor", "Performance Coach", "Project Manager", "Architect",
              "UI/UX Designer", "Business Consultant", "Backup Manager"]
    return {"agents": agents, "count": len(agents)}

app.include_router(router)
app.include_router(advanced_router)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Digital Castle API",
        version="3.0.0",
        description="Enterprise AI Agent System",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
