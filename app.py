import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import json
from datetime import datetime
from typing import Dict, Any

from config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_ID, PORT, WEBHOOK_URL,
    ANTHROPIC_API_KEY, DEEPSEEK_API_KEY, TOGETHER_API_KEY
)
from agent_router import HybridAgentRouter, router
from document_engine import DocumentEngine, doc_engine

# ================ LOGGING ================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/digital_castle.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ================ TELEGRAM UTILITIES ================
async def send_telegram_message(chat_id: int, text: str, parse_mode: str = "HTML"):
    """إرسال رسالة عبر Telegram Bot"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                logger.error(f"Failed to send Telegram message: {response.text}")
            else:
                logger.info(f"Message sent to {chat_id}")
    except Exception as e:
        logger.error(f"Telegram send error: {str(e)}")

async def send_admin_notification(message: str):
    """إرسال تنبيه للأدمن"""
    await send_telegram_message(TELEGRAM_ADMIN_ID, message)

# ================ LIFESPAN ================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """إدارة دورة حياة التطبيق"""
    
    logger.info("=" * 50)
    logger.info("🚀 Digital Castle S.P.C - Starting Up")
    logger.info("=" * 50)
    
    logger.info(f"TELEGRAM_BOT_TOKEN: {'✅' if TELEGRAM_BOT_TOKEN else '❌'}")
    logger.info(f"TELEGRAM_ADMIN_ID: {TELEGRAM_ADMIN_ID} {'✅' if TELEGRAM_ADMIN_ID else '❌'}")
    logger.info(f"ANTHROPIC_API_KEY: {'✅' if ANTHROPIC_API_KEY else '❌'}")
    
    app.state.router = router
    
    logger.info("✅ All Systems Ready")
    logger.info("=" * 50)
    
    try:
        await send_admin_notification("🟢 Digital Castle S.P.C - تم بدء التشغيل ✅")
    except Exception as e:
        logger.error(f"Failed to send startup notification: {e}")
    
    yield
    
    logger.info("🛑 Shutting Down")

# ================ FASTAPI APP ================
app = FastAPI(
    title="Digital Castle S.P.C",
    description="شركة القلعة الرقمية",
    version="1.0.0",
    lifespan=lifespan
)

# ================ ROUTES ================

@app.get("/")
async def root():
    logger.info("✅ Root accessed")
    return {"status": "online", "company": "Digital Castle S.P.C", "version": "1.0.0"}

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    logger.info("🔔 Webhook received")
    
    try:
        data = await request.json()
        logger.info(f"Data: {data}")
        
        if 'message' not in data:
            return JSONResponse({'ok': True})
        
        message = data['message']
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        text = message.get('text', '')
        
        logger.info(f"From: {user_id}, Chat: {chat_id}, Text: {text}")
        logger.info(f"Admin ID: {TELEGRAM_ADMIN_ID}")
        
        # التحقق من المسؤول
        if int(user_id) != int(TELEGRAM_ADMIN_ID):
            logger.warning(f"Unauthorized: {user_id}")
            await send_telegram_message(chat_id, "❌ غير مفوض")
            return JSONResponse({'ok': True})
        
        logger.info("✅ Authorized")
        
        # معالجة الأوامر
        if text == '/start':
            await send_telegram_message(chat_id, "🏰 أهلاً في Digital Castle\n\n/status - الحالة\n/tokens - التوكنز\n/help - المساعدة")
        
        elif text == '/status':
            token_summary = app.state.router.get_token_summary()
            status_msg = "📊 حالة النظام:\n\n"
            for provider, stats in token_summary.items():
                status_msg += f"{provider.upper()}: {stats['percentage']:.1f}%\n"
            await send_telegram_message(chat_id, status_msg)
        
        elif text == '/tokens':
            token_summary = app.state.router.get_token_summary()
            await send_telegram_message(chat_id, f"<pre>{json.dumps(token_summary, indent=2, ensure_ascii=False)}</pre>", "HTML")
        
        elif text == '/help':
            await send_telegram_message(chat_id, "🆘 المساعدة:\n\n/status\n/tokens\n/start")
        
        else:
            await send_telegram_message(chat_id, f"✅ استقبلت: {text}")
        
        logger.info("✅ Response sent")
        return JSONResponse({'ok': True})
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}", exc_info=True)
        return JSONResponse({'ok': False, 'error': str(e)})

@app.get("/api/tokens")
async def get_tokens():
    return app.state.router.get_token_summary()

# ================ MAIN ================
if __name__ == "__main__":
    import uvicorn
    os.makedirs('logs', exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
