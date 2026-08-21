import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

try:
    from telegram import Update
    from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
except ImportError:
    print("[Telegram Gateway] python-telegram-bot is not installed. Install with: pip install python-telegram-bot")

class TelegramGateway:
    def __init__(self, token: str = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN is not set.")

        from core.gemini_engine import GeminiAEAgent
        print("🧠 [Telegram Gateway] Initializing High-Intelligence Engine...")
        self.agent = GeminiAEAgent()
        print("✅ [Telegram Gateway] Engine Ready!")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("안녕하세요! Ezer Agent 텔레그램 게이트웨이가 활성화되었습니다. 무엇을 도와드릴까요?")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        if not user_text:
            return

        chat_id = str(update.effective_chat.id)
        print(f"📩 [Telegram Message] (Chat ID: {chat_id}): {user_text}")

        # Send typing action
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, self.agent.chat, user_text, f"telegram_{chat_id}")
            await update.message.reply_text(response)
        except Exception as e:
            await update.message.reply_text(f"⚠️ 오류가 발생했습니다: {e}")

    def run(self):
        print(f"🤖 [Ezer Agent] Starting Telegram Bot Gateway...")
        app = ApplicationBuilder().token(self.token).build()
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        app.run_polling()

if __name__ == "__main__":
    gw = TelegramGateway()
    gw.run()
