"""Telegram Bot Orchestrator"""
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from app.logging_config import get_logger

logger = get_logger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "test")
TELEGRAM_ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "0"))

class BotOrchestrator:
    def __init__(self):
        self.app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("status", self.status))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🏰 Digital Castle Ready")
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("✅ All systems running")
    
    def run(self):
        logger.info("🚀 Bot started")
        self.app.run_polling()

if __name__ == "__main__":
    bot = BotOrchestrator()
    bot.run()
