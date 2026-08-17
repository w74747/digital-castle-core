"""
خادم FastAPI الرئيسي مع Telegram Bot Integration
Main FastAPI server with Document Generation API
"""

import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio

from app.document_engine import DocumentEngine
from config.brand_settings import BRAND, validate_brand_config

# ============================================
# Logging Setup
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# FastAPI Initialization
# ============================================

app = FastAPI(
    title="Digital Castle S.P.C - Document Engine API",
    description=f"{BRAND.name_ar} | {BRAND.name_en}",
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Document Engine
try:
    doc_engine = DocumentEngine(template_path="config/invoice_template.html")
    logger.info("✅ Document Engine initialized successfully")
except FileNotFoundError as e:
    logger.error(f"❌ Failed to initialize Document Engine: {e}")
    doc_engine = None

# ============================================
# Environment Variables
# ============================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ADMIN_ID = os.getenv("TELEGRAM_ADMIN_ID", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")

# ============================================
# Pydantic Models
# ============================================

class InvoiceItem(BaseModel):
    description: str
    quantity: float
    unit_price: float


class InvoiceRequest(BaseModel):
    invoice_number: str
    client_name: str
    client_contact: str
    items: List[InvoiceItem]


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str
    version: str
    components: dict


# ============================================
# Routes
# ============================================

@app.on_event("startup")
async def startup_event():
    """استدعاء التطبيق"""
    if not validate_brand_config():
        logger.error("❌ Brand configuration is incomplete")
        raise RuntimeError("Invalid brand configuration")
    
    logger.info("=" * 60)
    logger.info(f"🚀 {BRAND.name_ar} ({BRAND.name_en})")
    logger.info("=" * 60)
    logger.info(f"📄 Document Engine: {'✅ Ready' if doc_engine else '❌ Failed'}")
    logger.info(f"🔐 Telegram Bot: {'✅ Configured' if TELEGRAM_BOT_TOKEN else '⚠️ Not configured'}")
    logger.info(f"🔑 API Keys: {sum([bool(x) for x in [ANTHROPIC_API_KEY, DEEPSEEK_API_KEY]])}/2 configured")
    logger.info("=" * 60)


@app.get("/", tags=["Health"], response_model=HealthResponse)
async def root():
    """فحص صحة النظام - Health Check"""
    return HealthResponse(
        status="operational",
        timestamp=datetime.now().isoformat(),
        service=BRAND.name_en,
        version="2.0.0",
        components={
            "document_engine": "✅" if doc_engine else "❌",
            "telegram_integration": "✅" if TELEGRAM_BOT_TOKEN else "⚠️",
            "database": "✅" if DATABASE_URL else "⚠️",
            "brand_config": "✅" if validate_brand_config() else "❌"
        }
    )


@app.post("/api/v1/invoice/generate", tags=["Invoice"])
async def generate_invoice(request: InvoiceRequest):
    """
    توليد فاتورة رسمية بصيغة PDF
    Generate official invoice PDF
    
    Example:
```json
    {
        "invoice_number": "INV-2026-001",
        "client_name": "عميل الاختبار",
        "client_contact": "contact@example.com",
        "items": [
            {"description": "خدمة تطوير", "quantity": 5, "unit_price": 100.0},
            {"description": "استشارة فنية", "quantity": 2, "unit_price": 150.0}
        ]
    }
```
    """
    if not doc_engine:
        raise HTTPException(status_code=503, detail="Document engine not available")
    
    try:
        # تحويل Pydantic models إلى dict
        items_data = [
            {
                "description": item.description,
                "quantity": item.quantity,
                "unit_price": item.unit_price
            }
            for item in request.items
        ]
        
        # توليد PDF
        pdf_buffer = await doc_engine.generate_invoice_pdf(
            invoice_number=request.invoice_number,
            client_name=request.client_name,
            client_contact=request.client_contact,
            items=items_data
        )
        
        logger.info(f"✅ Invoice generated: {request.invoice_number}")
        
        return FileResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            filename=f"Invoice_{request.invoice_number}.pdf",
            headers={"Content-Disposition": f"attachment; filename='Invoice_{request.invoice_number}.pdf'"}
        )
    
    except Exception as e:
        logger.error(f"❌ Error generating invoice: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.get("/api/v1/invoice/sample", tags=["Invoice"])
async def get_sample_invoice():
    """
    تحميل فاتورة تجريبية
    Download sample invoice
    """
    if not doc_engine:
        raise HTTPException(status_code=503, detail="Document engine not available")
    
    try:
        sample_items = [
            {"description": "خدمات تطوير وتكامل سحابي", "quantity": 1, "unit_price": 250.0},
            {"description": "إعداد بيئة الوكلاء والذكاء الاصطناعي", "quantity": 1, "unit_price": 150.0},
            {"description": "اختبار الجودة والأداء", "quantity": 1, "unit_price": 100.0}
        ]
        
        pdf_buffer = await doc_engine.generate_invoice_pdf(
            invoice_number="INV-2026-SAMPLE",
            client_name="عميل تجريبي",
            client_contact="sample@example.com",
            items=sample_items
        )
        
        return FileResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            filename="Digital_Castle_Sample_Invoice.pdf"
        )
    
    except Exception as e:
        logger.error(f"❌ Error generating sample invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/config", tags=["Configuration"])
async def get_config():
    """الحصول على معايير الهوية"""
    return {
        "status": "success",
        "brand": {
            "name_ar": BRAND.name_ar,
            "name_en": BRAND.name_en,
            "tagline_ar": BRAND.tagline_ar,
            "email": BRAND.email,
            "currency": BRAND.currency,
            "tax_rate": BRAND.tax_rate,
            "colors": {
                "primary": BRAND.color_primary,
                "secondary": BRAND.color_secondary,
                "accent": BRAND.color_accent
            }
        },
        "assets": {
            "logo": os.path.exists("assets/logo.png"),
            "signature": os.path.exists("assets/signature.png"),
            "stamp": os.path.exists("assets/stamp.png")
        }
    }


# ============================================
# Error Handlers
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """معالج الأخطاء العام"""
    logger.error(f"❌ Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
