"""
Digital Castle S.P.C - FastAPI Application
البنية التحتية الأساسية والخادم الرئيسي
"""

import logging
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from document_engine import DocumentEngine

# =====================================
# LOGGING CONFIGURATION
# =====================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =====================================
# GLOBAL STATE & ENGINE
# =====================================
document_engine: DocumentEngine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    إدارة دورة حياة التطبيق
    - عند البدء: تهيئة محرك المستندات
    - عند الإغلاق: تنظيف الموارد
    """
    global document_engine
    logger.info("🚀 Starting Digital Castle S.P.C Application...")
    
    try:
        document_engine = DocumentEngine()
        logger.info("✅ Document Engine initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Document Engine: {e}")
        raise
    
    yield
    
    logger.info("🛑 Shutting down Digital Castle S.P.C Application...")
    # تنظيف الموارد إن لزم الأمر
    document_engine = None

# =====================================
# FASTAPI APP INITIALIZATION
# =====================================
app = FastAPI(
    title="Digital Castle S.P.C - API",
    description="Core Infrastructure & Document Generation Engine (Phase 1)",
    version="1.0.0",
    lifespan=lifespan
)

# =====================================
# CORS MIDDLEWARE
# =====================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================
# STATIC FILES
# =====================================
assets_path = Path(__file__).parent / "assets"
if assets_path.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")

# =====================================
# PYDANTIC MODELS
# =====================================
class InvoiceItem(BaseModel):
    """موديل عنصر الفاتورة"""
    description: str
    quantity: float
    unit_price: float
    amount: float

class InvoiceRequest(BaseModel):
    """موديل طلب الفاتورة"""
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

class HealthResponse(BaseModel):
    """موديل استجابة الصحة"""
    status: str
    timestamp: str
    version: str
    service: str

# =====================================
# HEALTH CHECK ENDPOINTS
# =====================================
@app.get("/", tags=["Health"])
async def root() -> Dict[str, Any]:
    """
    📌 Health Check - نقطة الاختبار الأساسية
    """
    return HealthResponse(
        status="online",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        service="Digital Castle S.P.C - Phase 1: Core Infrastructure"
    ).model_dump()

@app.get("/health", tags=["Health"])
async def health_check() -> HealthResponse:
    """
    📌 Health Check Endpoint - فحص صحة الخادم
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        service="Digital Castle S.P.C"
    )

# =====================================
# DOCUMENT GENERATION ENDPOINTS
# =====================================
@app.get("/api/v1/invoice/sample", tags=["Documents"])
async def generate_sample_invoice():
    """
    📄 Sample Invoice Generation
    توليد فاتورة تجريبية PDF للاختبار
    """
    if document_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Document Engine not initialized"
        )
    
    try:
        logger.info("📋 Generating sample invoice...")
        pdf_bytes = document_engine.generate_sample_invoice()
        
        return FileResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=DC-2024-000001-SAMPLE.pdf"
            }
        )
    except Exception as e:
        logger.error(f"❌ Error generating sample invoice: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/invoice/generate", tags=["Documents"])
async def generate_custom_invoice(invoice_data: InvoiceRequest):
    """
    📄 Custom Invoice Generation
    توليد فاتورة مخصصة بناءً على البيانات المرسلة
    """
    if document_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Document Engine not initialized"
        )
    
    try:
        logger.info(f"📋 Generating custom invoice: {invoice_data.invoice_number}")
        
        # تحويل البيانات إلى dictionary
        invoice_dict = invoice_data.model_dump()
        invoice_dict['items'] = [
            item.model_dump() for item in invoice_data.items
        ]
        
        # توليد PDF
        pdf_bytes = document_engine.generate_invoice_pdf(invoice_dict)
        
        return FileResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={invoice_data.invoice_number}.pdf"
            }
        )
    except ValueError as ve:
        logger.error(f"❌ Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"❌ Error generating invoice: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================
# SYSTEM INFO ENDPOINTS
# =====================================
@app.get("/api/v1/system/brand", tags=["System"])
async def get_brand_guidelines():
    """
    🎨 Brand Guidelines
    إرجاع معايير الهوية والألوان الرسمية
    """
    if document_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Document Engine not initialized"
        )
    
    return JSONResponse(
        content=document_engine.brand_guidelines,
        media_type="application/json"
    )

@app.get("/api/v1/system/info", tags=["System"])
async def system_info():
    """
    ℹ️ System Information
    معلومات النظام والتطبيق
    """
    return {
        "company": "Digital Castle S.P.C",
        "company_ar": "شركة القلعة الرقمية ش.ش.و",
        "phase": 1,
        "phase_name": "Core Infrastructure & Document Engine",
        "endpoints": {
            "health": "/health",
            "sample_invoice": "/api/v1/invoice/sample",
            "custom_invoice": "/api/v1/invoice/generate",
            "brand_guidelines": "/api/v1/system/brand",
            "api_docs": "/docs",
            "api_openapi": "/openapi.json"
        }
    }

# =====================================
# ERROR HANDLERS
# =====================================
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """معالج الأخطاء العامة"""
    logger.error(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": type(exc).__name__
        }
    )

# =====================================
# STARTUP & SHUTDOWN EVENTS
# =====================================
@app.on_event("startup")
async def startup_event():
    """عند بدء التطبيق"""
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("🏰 Digital Castle S.P.C - Phase 1 Activated")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

@app.on_event("shutdown")
async def shutdown_event():
    """عند إيقاف التطبيق"""
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("🔒 Digital Castle S.P.C - Shutdown Complete")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# =====================================
# RUN CONFIGURATION
# =====================================
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
