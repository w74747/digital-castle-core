import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from io import BytesIO
from datetime import datetime, timedelta

# Import DocumentEngine
from document_engine import DocumentEngine, InvoiceData, InvoiceItem, create_sample_invoice

# ============================================
# Configuration & Logging
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# FastAPI App Initialization
# ============================================

app = FastAPI(
    title="Digital Castle S.P.C - Document Engine API",
    description="منصة توليد المستندات الرسمية والفواتير | Official Document Generation Platform",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Document Engine
document_engine = DocumentEngine(base_path=".")

# ============================================
# Environment Variables
# ============================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ADMIN_ID = os.getenv("TELEGRAM_ADMIN_ID", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")

logger.info("✅ Environment variables loaded from Railway")

# ============================================
# Pydantic Models
# ============================================

class HealthCheck(BaseModel):
    status: str
    version: str
    timestamp: str
    components: dict


class InvoiceRequest(BaseModel):
    invoice_number: str
    client_name: str
    client_email: str
    client_address: str
    items: list  # List of {"description", "quantity", "unit_price"}
    tax_rate: float = 5.0
    days_until_due: int = 30


# ============================================
# Routes
# ============================================

@app.on_event("startup")
async def startup_event():
    """استدعاء التطبيق"""
    logger.info("🚀 Digital Castle S.P.C Document Engine starting...")
    logger.info(f"📂 Base path: {os.getcwd()}")
    logger.info(f"🔐 Telegram Bot Token: {'✅ Configured' if TELEGRAM_BOT_TOKEN else '❌ Not configured'}")
    logger.info(f"🔐 API Keys: {sum([bool(x) for x in [ANTHROPIC_API_KEY, DEEPSEEK_API_KEY, TOGETHER_API_KEY]])}/3 configured")


@app.on_event("shutdown")
async def shutdown_event():
    """إيقاف التطبيق"""
    logger.info("🛑 Digital Castle S.P.C Document Engine shutting down...")


@app.get("/", tags=["Health"])
async def root():
    """Health check و معلومات التطبيق"""
    return HealthCheck(
        status="operational",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
        components={
            "document_engine": "✅ Initialized",
            "jinja2_templates": "✅ Loaded",
            "weasyprint": "✅ Ready",
            "telegram_bot": "✅ Connected" if TELEGRAM_BOT_TOKEN else "⚠️ Not configured",
            "github_integration": "✅ Ready" if GITHUB_TOKEN else "⚠️ Not configured",
            "database": "✅ Connected" if DATABASE_URL else "⚠️ Not configured"
        }
    )


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """فحص صحة النظام"""
    return {
        "status": "healthy",
        "service": "Digital Castle S.P.C Document Engine",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "document_engine": True,
            "templates": True,
            "assets": os.path.exists("assets"),
            "brand_kit": os.path.exists("brand-kit")
        }
    }


@app.get("/api/v1/invoice/sample", tags=["Invoice"])
async def get_sample_invoice():
    """
    الحصول على فاتورة تجريبية بصيغة PDF
    
    Returns:
        PDF file with sample invoice
    """
    try:
        # إنشاء فاتورة تجريبية
        sample_invoice = create_sample_invoice()
        
        # توليد PDF
        pdf_io = document_engine.generate_invoice_pdf(sample_invoice)
        
        return FileResponse(
            iter([pdf_io.getvalue()]),
            media_type="application/pdf",
            filename="Digital_Castle_Sample_Invoice.pdf",
            headers={"Content-Disposition": "attachment; filename='Digital_Castle_Sample_Invoice.pdf'"}
        )
    
    except Exception as e:
        logger.error(f"❌ Error generating sample invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/invoice/generate", tags=["Invoice"])
async def generate_invoice(request: InvoiceRequest):
    """
    توليد فاتورة مخصصة
    
    Example request:
```json
    {
        "invoice_number": "INV-2025-002",
        "client_name": "عميل الاختبار",
        "client_email": "test@example.com",
        "client_address": "مسقط، سلطنة عمان",
        "items": [
            {"description": "خدمة استشارية", "quantity": 5, "unit_price": 100.0},
            {"description": "تطوير برمجي", "quantity": 20, "unit_price": 75.0}
        ],
        "tax_rate": 5.0,
        "days_until_due": 30
    }
```
    """
    try:
        # تحويل البيانات إلى InvoiceData
        items = [
            InvoiceItem(
                description=item["description"],
                quantity=float(item["quantity"]),
                unit_price=float(item["unit_price"])
            )
            for item in request.items
        ]
        
        issue_date = datetime.now()
        due_date = issue_date + timedelta(days=request.days_until_due)
        
        invoice_data = InvoiceData(
            invoice_number=request.invoice_number,
            issue_date=issue_date.strftime("%Y-%m-%d"),
            due_date=due_date.strftime("%Y-%m-%d"),
            client_name=request.client_name,
            client_email=request.client_email,
            client_address=request.client_address,
            items=items,
            tax_rate=request.tax_rate
        )
        
        # توليد PDF
        pdf_io = document_engine.generate_invoice_pdf(invoice_data)
        
        return FileResponse(
            iter([pdf_io.getvalue()]),
            media_type="application/pdf",
            filename=f"Invoice_{request.invoice_number}.pdf",
            headers={"Content-Disposition": f"attachment; filename='Invoice_{request.invoice_number}.pdf'"}
        )
    
    except Exception as e:
        logger.error(f"❌ Error generating invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/invoice/preview", tags=["Invoice"])
async def preview_sample_invoice():
    """معاينة الفاتورة التجريبية بصيغة HTML"""
    try:
        sample_invoice = create_sample_invoice()
        html_content = document_engine.generate_invoice_html(sample_invoice)
        
        return {
            "status": "success",
            "invoice_number": sample_invoice.invoice_number,
            "html_content": html_content,
            "metadata": {
                "total": sample_invoice.total,
                "subtotal": sample_invoice.subtotal,
                "tax": sample_invoice.tax_amount,
                "items_count": len(sample_invoice.items)
            }
        }
    
    except Exception as e:
        logger.error(f"❌ Error previewing invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/config", tags=["Config"])
async def get_config():
    """الحصول على معايير الهوية والإعدادات"""
    try:
        return {
            "status": "success",
            "brand": document_engine.brand_guidelines,
            "components": {
                "logo": os.path.exists(os.path.join("assets", "logo.svg")),
                "signature": os.path.exists(os.path.join("assets", "signature.png")),
                "stamp": os.path.exists(os.path.join("assets", "stamp.png")),
                "templates": os.path.exists(os.path.join("brand-kit", "templates"))
            }
        }
    
    except Exception as e:
        logger.error(f"❌ Error loading config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Error Handling
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """معالج الأخطاء العام"""
    logger.error(f"❌ Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)}
    )


# ============================================
# 404 Handler
# ============================================

@app.get("/{path:path}", tags=["Fallback"])
async def fallback(path: str):
    """معالج المسارات غير الموجودة"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": f"Endpoint '/{path}' not found",
            "available_endpoints": {
                "health": "GET /",
                "health_check": "GET /api/v1/health",
                "sample_invoice": "GET /api/v1/invoice/sample",
                "generate_invoice": "POST /api/v1/invoice/generate",
                "preview_invoice": "GET /api/v1/invoice/preview",
                "config": "GET /api/v1/config"
            }
        }
    )


# ============================================
# Lifespan Context Manager
# ============================================

@app.middleware("http")
async def log_requests(request, call_next):
    """تسجيل جميع الطلبات"""
    logger.info(f"📨 Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"📤 Response: {response.status_code}")
    return response


if __name__ == "__main__":
    import uvicorn
    
    # تشغيل الخادم على Railway
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
