import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎉 Bot đã triển khai thành công trên Render!")

async def main():
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        await app.run_polling()
    except Exception as e:
        print("Lỗi khi chạy bot:", e)
        await asyncio.sleep(10)  # đợi rồi thử lại hoặc thoát

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
