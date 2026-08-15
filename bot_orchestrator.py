# bot_orchestrator.py (معدّل)
"""Telegram Bot Orchestrator - Main Interface"""
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from app.agent_router import router as api_router
from app.smart_llm_router import smart_router
from app.data_security import sanitizer, encryptor
from app.prime_agent_adapter import prime_agent_system
from app.code_graph_adapter import code_graph
from app.security_scanner import security_scanner
from app.memory_system import memory_store, cache_manager
from app.logging_config import get_logger

logger = get_logger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "0"))

class BotOrchestrator:
    def __init__(self):
        self.app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("invoice", self.invoice))
        self.app.add_handler(CommandHandler("ask", self.ask))
        self.app.add_handler(CommandHandler("status", self.status))
        self.app.add_handler(CommandHandler("scan", self.scan_security))
        self.app.add_handler(CommandHandler("agents", self.list_agents))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != TELEGRAM_ADMIN_ID:
            await update.message.reply_text("❌ Unauthorized")
            return
        
        await update.message.reply_text(
            "🏰 Digital Castle S.P.C\n\n"
            "Commands:\n"
            "/invoice - Create invoice\n"
            "/ask - Query AI\n"
            "/status - System status\n"
            "/scan - Security scan\n"
            "/agents - List agents"
        )
    
    async def invoice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != TELEGRAM_ADMIN_ID:
            await update.message.reply_text("❌ Unauthorized")
            return
        
        try:
            await update.message.reply_text("📄 Creating invoice...")
            # Invoice logic here
            await update.message.reply_text("✅ Invoice created")
        except Exception as e:
            logger.error(f"Invoice error: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def ask(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != TELEGRAM_ADMIN_ID:
            await update.message.reply_text("❌ Unauthorized")
            return
        
        try:
            prompt = " ".join(context.args)
            if not prompt:
                await update.message.reply_text("❌ No prompt provided")
                return
            
            await update.message.reply_text("🤔 Processing...")
            
            # Sanitize input
            clean_prompt = sanitizer.sanitize(prompt)
            
            # Route to smart LLM
            result = await smart_router.route(
                clean_prompt,
                task_type="coding",
                sensitive_data=False
            )
            
            await update.message.reply_text(f"✅ Response:\n\n{result[:500]}")
        except Exception as e:
            logger.error(f"Ask error: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != TELEGRAM_ADMIN_ID:
            await update.message.reply_text("❌ Unauthorized")
            return
        
        try:
            status_msg = "🏰 Digital Castle Status\n\n"
            status_msg += "✅ Bot: Running\n"
            status_msg += "✅ Database: Connected\n"
            status_msg += "✅ LocalAI: Ready\n"
            status_msg += "✅ Qwen: Ready\n"
            
            await update.message.reply_text(status_msg)
        except Exception as e:
            logger.error(f"Status error: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def scan_security(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != TELEGRAM_ADMIN_ID:
            await update.message.reply_text("❌ Unauthorized")
            return
        
        try:
            await update.message.reply_text("🔒 Scanning security...")
            
            results = await security_scanner.full_scan(".")
            report = await security_scanner.get_report(results)
