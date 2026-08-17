#!/usr/bin/env python3
"""
app.py - FastAPI Application with Correct Paths
Digital Castle S.P.C - Document Engine
"""

import os
import logging
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Digital Castle - Document Engine",
    description="Invoice Generation API",
    version="1.0.0"
)

# Initialize Document Engine with CORRECT PATHS
try:
    from app.document_engine import DocumentEngine
    
    # ✅ CORRECT PATHS
    engine = DocumentEngine(
        template_path="brand-kit/templates/invoice.html",
        brand_guidelines_path="brand-kit/brand_guidelines.json",
        assets_path="assets"
    )
    logger.info("✅ DocumentEngine initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Document Engine: {e}")
    engine = None

# ============================================
# Pydantic Models
# ============================================

class InvoiceItem(BaseModel):
    """Invoice line item"""
    description: str
    quantity: float
    unit_price: float


class InvoiceRequest(BaseModel):
    """Invoice generation request"""
    invoice_number: str
    client_name: str
    client_email: str
    client_contact: str
    items: List[InvoiceItem]
    issue_date: Optional[str] = None
    due_date: Optional[str] = None


# ============================================
# Routes
# ============================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "message": "Digital Castle - Document Engine API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    logger.info("✅ Health check")
    return {
        "status": "healthy",
        "version": "1.0.0",
        "message": "Digital Castle Document Engine is running",
        "engine_status": "ready" if engine else "not initialized"
    }


@app.post("/api/invoices/generate", tags=["Invoices"])
async def generate_invoice(request: InvoiceRequest):
    """
    Generate an invoice
    """
    try:
        if not engine:
            raise HTTPException(
                status_code=503, 
                detail="DocumentEngine not initialized. Check template and brand guidelines paths."
            )
        
        logger.info(f"📄 Generating invoice: {request.invoice_number}")
        
        # Prepare items
        items = [
            {
                "description": item.description,
                "quantity": item.quantity,
                "unit_price": item.unit_price
            }
            for item in request.items
        ]
        
        # Generate PDF
        pdf = await engine.generate_invoice_pdf(
            invoice_number=request.invoice_number,
            client_name=request.client_name,
            client_email=request.client_email,
            client_contact=request.client_contact,
            items=items,
            issue_date=request.issue_date,
            due_date=request.due_date
        )
        
        logger.info(f"✅ Invoice generated: {request.invoice_number}")
        
        return {
            "status": "success",
            "invoice_number": request.invoice_number,
            "message": "Invoice generated successfully",
            "pdf_size": len(pdf.getvalue())
        }
    
    except Exception as e:
        logger.error(f"❌ Error generating invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status", tags=["Status"])
async def status():
    """Get API status"""
    logger.info("📊 Status check")
    return {
        "service": "Document Engine API",
        "status": "operational" if engine else "degraded",
        "version": "1.0.0",
        "components": {
            "invoice_generation": "✅ ready" if engine else "❌ not ready",
            "pdf_engine": "✅ ready" if engine else "❌ not ready",
            "assets": "✅ integrated" if engine else "❌ not ready"
        },
        "paths": {
            "template": "brand-kit/templates/invoice.html",
            "brand_guidelines": "brand-kit/brand_guidelines.json",
            "assets": "assets/"
        }
    }


# ============================================
# Startup Event
# ============================================

@app.on_event("startup")
async def startup_event():
    """On startup"""
    logger.info("=" * 60)
    logger.info("🚀 Digital Castle - Document Engine API")
    logger.info("=" * 60)
    
    if engine:
        logger.info("✅ Document Engine: Ready")
    else:
        logger.warning("❌ Document Engine: Not initialized")
    
    logger.info("📖 Docs: /docs")
    logger.info("📊 Status: /api/status")
    logger.info("=" * 60)


# ============================================
# Main
# ============================================

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    
    # Run server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
