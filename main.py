import os
import json
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Lấy token từ biến môi trường
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Tạo thư mục lưu file nếu chưa có
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def get_user_file(user_id):
    return os.path.join(DATA_DIR, f"{user_id}.json")

def load_data(user_id):
    filepath = get_user_file(user_id)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(user_id, data):
    filepath = get_user_file(user_id)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Chào bạn! Tôi là bot quản lý tài chính.\n"
        "Ghi chi tiêu: /add 50000 cơm trưa\n"
        "Ghi thu nhập: /income 300000 lương\n"
        "Xem báo cáo: /report"
    )

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.replace("/add", "").strip()

    try:
        amount_str, *note_parts = text.split()
        amount = int(amount_str)
        note = " ".join(note_parts)
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        entry = {"type": "expense", "amount": amount, "note": note, "time": now}

        data = load_data(user_id)
        data.append(entry)
        save_data(user_id, data)

        await update.message.reply_text(f"📝 Đã ghi chi tiêu: {amount}đ - {note}")
    except:
        await update.message.reply_text("❌ Sai cú pháp! Dùng: /add 50000 cơm trưa")

async def add_income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.replace("/income", "").strip()

    try:
        amount_str, *note_parts = text.split()
        amount = int(amount_str)
        note = " ".join(note_parts)
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        entry = {"type": "income", "amount": amount, "note": note, "time": now}

        data = load_data(user_id)
        data.append(entry)
        save_data(user_id, data)

        await update.message.reply_text(f"💰 Đã ghi thu nhập: {amount}đ - {note}")
    except:
        await update.message.reply_text("❌ Sai cú pháp! Dùng: /income 300000 lương tháng")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    data = load_data(user_id)
    if not data:
        await update.message.reply_text("📭 Bạn chưa có ghi chép nào.")
        return

    income = sum(x["amount"] for x in data if x["type"] == "income")
    expense = sum(x["amount"] for x in data if x["type"] == "expense")
    balance = income - expense

    lines = [
        f'{x["time"]}: {x["amount"]}đ - {x["note"]} ({x["type"]})'
        for x in data[-5:]
    ]

    response = "\n".join(lines)
    response += f"\n\n📊 Báo cáo:\n- Thu nhập: {income}đ\n- Chi tiêu: {expense}đ\n- Số dư: {balance}đ"

    await update.message.reply_text(response)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_expense))
    app.add_handler(CommandHandler("income", add_income))
    app.add_handler(CommandHandler("report", report))

    app.run_polling()
