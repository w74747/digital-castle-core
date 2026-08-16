"""
Digital Castle S.P.C - FastAPI Application
البنية التحتية المتكاملة مع Telegram Bot و Agent Router
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from config import settings
from document_engine import DocumentEngine, get_document_engine
from agent_router import get_agent_router, TaskType, AgentType
from telegram_handler import get_telegram_handler
from pydantic import BaseModel

# =====================================
# LOGGING
# =====================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =====================================
# GLOBAL STATE
# =====================================
telegram_handler = None
document_engine = None
agent_router = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """دورة حياة التطبيق"""
    
    # STARTUP
    logger.info("🚀 Starting Digital Castle S.P.C Application...")
    
    # التحقق من المتغيرات
    if not settings.validate_keys():
        logger.warning("⚠️ Some environment variables are missing!")
    
    try:
        global document_engine, agent_router, telegram_handler
        
        # تهيئة محرك المستندات
        document_engine = get_document_engine()
        logger.info("✅ Document Engine initialized")
        
        # تهيئة موجه الوكلاء
        agent_router = await get_agent_router()
        logger.info("✅ Agent Router initialized")
        
        # تهيئة معالج Telegram
        telegram_handler = await get_telegram_handler()
        await telegram_handler.initialize()
        logger.info("✅ Telegram Handler initialized")
        
        # بدء Telegram Bot في خيط منفصل
        asyncio.create_task(telegram_handler.start())
        logger.info("✅ Telegram Bot started")
        
    except Exception as e:
        logger.error(f"❌ Initialization error: {e}")
        raise
    
    yield
    
    # SHUTDOWN
    logger.info("🛑 Shutting down Digital Castle S.P.C...")
    if telegram_handler:
        await telegram_handler.stop()


# =====================================
# FASTAPI APP
# =====================================
app = FastAPI(
    title="Digital Castle S.P.C - API",
    description="Core Infrastructure & Document Engine with Multi-Agent System",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files
assets_path = Path(__file__).parent / "assets"
if assets_path.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")

# =====================================
# PYDANTIC MODELS
# =====================================
class InvoiceItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    amount: float


class InvoiceRequest(BaseModel):
    invoice_number: str
    date: str
    due_date: str
    currency: str = "OMR"
    client_name: str
    client_email: str
    client_phone: str
    client_address: str
    items: list[InvoiceItem]
    tax_rate: float = 0
    discount: float = 0
    notes: str = ""


class AgentTaskRequest(BaseModel):
    task_type: str
    prompt: str
    context: dict = {}
    max_tokens: int = 1000


# =====================================
# HEALTH CHECK
# =====================================
@app.get("/", tags=["Health"])
async def root():
    """Health Check - نقطة الاختبار الأساسية"""
    return {
        "status": "online",
        "service": settings.COMPANY_NAME,
        "phase": f"{settings.PHASE} - {settings.PHASE_NAME}",
        "version": settings.APP_VERSION
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health Check Endpoint"""
    return {
        "status": "healthy",
        "components": {
            "api": "✅",
            "document_engine": "✅" if document_engine else "❌",
            "agent_router": "✅" if agent_router else "❌",
            "telegram": "✅" if telegram_handler else "❌"
        }
    }


# =====================================
# INVOICE ENDPOINTS
# =====================================
@app.get("/api/v1/invoice/sample", tags=["Documents"])
async def generate_sample_invoice():
    """Sample Invoice Generation"""
    if not document_engine:
        raise HTTPException(status_code=503, detail="Document Engine not ready")
    
    try:
        logger.info("📋 Generating sample invoice...")
        pdf_bytes = document_engine.generate_sample_invoice()
        
        return FileResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=DC-2024-000001-SAMPLE.pdf"}
        )
    except Exception as e:
        logger.error(f"❌ Invoice generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/invoice/generate", tags=["Documents"])
async def generate_custom_invoice(invoice_data: InvoiceRequest):
    """Custom Invoice Generation"""
    if not document_engine:
        raise HTTPException(status_code=503, detail="Document Engine not ready")
    
    try:
        logger.info(f"📋 Generating invoice: {invoice_data.invoice_number}")
        
        invoice_dict = invoice_data.model_dump()
        invoice_dict['items'] = [item.model_dump() for item in invoice_data.items]
        
        pdf_bytes = document_engine.generate_invoice_pdf(invoice_dict)
        
        return FileResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={invoice_data.invoice_number}.pdf"}
        )
    except Exception as e:
        logger.error(f"❌ Invoice error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================
# AGENT ENDPOINTS
# =====================================
@app.post("/api/v1/agents/task", tags=["Agents"])
async def submit_agent_task(task_request: AgentTaskRequest):
    """
    Submit a task to the multi-agent system
    تقديم مهمة للنظام متعدد الوكلاء
    """
    if not agent_router:
        raise HTTPException(status_code=503, detail="Agent Router not ready")
    
    try:
        logger.info(f"🤖 Task submitted: {task_request.task_type}")
        
        task_type = TaskType(task_request.task_type)
        
        response = await agent_router.route_task(
            task_type=task_type,
            prompt=task_request.prompt,
            context=task_request.context,
            max_tokens=task_request.max_tokens
        )
        
        return {
            "status": "completed",
            "agent": response.agent_type.value,
            "task_type": response.task_type.value,
            "model": response.model_used,
            "tokens_used": response.tokens_used,
            "timestamp": response.timestamp,
            "content": response.content
        }
    
    except Exception as e:
        logger.error(f"❌ Agent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/agents/stats", tags=["Agents"])
async def get_agent_stats():
    """Get agent system statistics"""
    if not agent_router:
        raise HTTPException(status_code=503, detail="Agent Router not ready")
    
    stats = await agent_router.get_router_stats()
    return stats


# =====================================
# SYSTEM ENDPOINTS
# =====================================
@app.get("/api/v1/system/brand", tags=["System"])
async def get_brand_guidelines():
    """Brand Guidelines - معايير الهوية"""
    if not document_engine:
        raise HTTPException(status_code=503, detail="Document Engine not ready")
    
    return JSONResponse(content=document_engine.brand_guidelines)


@app.get("/api/v1/system/info", tags=["System"])
async def system_info():
    """System Information"""
    return {
        "company": settings.COMPANY_NAME,
        "company_ar": settings.COMPANY_NAME_AR,
        "phase": settings.PHASE,
        "phase_name": settings.PHASE_NAME,
        "version": settings.APP_VERSION,
        "endpoints": {
            "health": "/health",
            "invoice_sample": "/api/v1/invoice/sample",
            "invoice_generate": "/api/v1/invoice/generate",
            "agent_task": "/api/v1/agents/task",
            "agent_stats": "/api/v1/agents/stats",
            "brand": "/api/v1/system/brand",
            "api_docs": "/docs"
        }
    }


@app.get("/api/v1/system/config", tags=["System"])
async def system_config():
    """System Configuration (Admin only)"""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "phase": settings.PHASE,
        "database": "configured" if settings.DATABASE_URL else "not configured",
        "apis": {
            "anthropic": "✅" if settings.ANTHROPIC_API_KEY else "❌",
            "deepseek": "✅" if settings.DEEPSEEK_API_KEY else "❌",
            "together": "✅" if settings.TOGETHER_API_KEY else "❌",
            "telegram": "✅" if settings.TELEGRAM_BOT_TOKEN else "❌"
        }
    }


# =====================================
# STARTUP/SHUTDOWN
# =====================================
@app.on_event("startup")
async def startup_event():
    logger.info("━" * 50)
    logger.info("🏰 Digital Castle S.P.C - Activated")
    logger.info("━" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("━" * 50)
    logger.info("🔒 Digital Castle S.P.C - Shutdown Complete")
    logger.info("━" * 50)


# =====================================
# IMPORT MISSING
# =====================================
import io

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
