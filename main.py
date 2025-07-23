import json
import os
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

TOKEN = os.getenv("TELEGRAM_TOKEN")  # hoặc gán trực tiếp: "123456:ABC-..."

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Chào bạn! Đây là bot quản lý thu nhập và chi tiêu.\nDùng /help để xem hướng dẫn."
    )

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/addin SỐTIỀN GHI_CHÚ – Ghi thu nhập\n"
        "/addout SỐTIỀN GHI_CHÚ – Ghi chi tiêu\n"
        "/report – Xem báo cáo hôm nay"
    )

# Ghi thu nhập
async def add_income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await save_entry(update, context, entry_type="income")

# Ghi chi tiêu
async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await save_entry(update, context, entry_type="expense")

# Lưu dữ liệu (thu/chi)
async def save_entry(update: Update, context: ContextTypes.DEFAULT_TYPE, entry_type: str):
    try:
        user_id = str(update.message.from_user.id)
        file_name = f"data_{user_id}.json"
        text = " ".join(context.args)
        amount_str, *note_parts = text.split()
        amount = int(amount_str)
        note = " ".join(note_parts)

        entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "amount": amount,
            "note": note,
            "type": entry_type
        }

        data = []
        if os.path.exists(file_name):
            with open(file_name, "r", encoding="utf-8") as f:
                data = json.load(f)

        data.append(entry)

        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        prefix = "+" if entry_type == "income" else "-"
        await update.message.reply_text(f"✅ Đã ghi {entry_type}: {prefix}{amount} đ - {note}")
    except:
        await update.message.reply_text(
            "⚠ Sai cú pháp.\nVí dụ:\n/addin 500000 lương\n/addout 20000 ăn sáng"
        )

# /report – Báo cáo thu/chi hôm nay
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    file_name = f"data_{user_id}.json"
    today = datetime.now().strftime("%Y-%m-%d")

    if not os.path.exists(file_name):
        await update.message.reply_text("📭 Bạn chưa có dữ liệu.")
        return

    with open(file_name, "r", encoding="utf-8") as f:
        data = json.load(f)

    income_total = 0
    expense_total = 0
    lines = []

    for item in data:
        if item["date"] == today:
            amount = item["amount"]
            note = item["note"]
            if item["type"] == "income":
                income_total += amount
                lines.append(f"💰 +{amount} đ - {note}")
            else:
                expense_total += amount
                lines.append(f"💸 -{amount} đ - {note}")

    if not lines:
        await update.message.reply_text("📅 Hôm nay bạn chưa ghi thu/chi nào.")
        return

    balance = income_total - expense_total
    message = "\n".join(lines)
    message += f"\n\n📊 Tổng thu: +{income_total} đ\n📉 Tổng chi: -{expense_total} đ\n💼 Số dư: {balance} đ"
    await update.message.reply_text(message)

# Main
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("addin", add_income))
    app.add_handler(CommandHandler("addout", add_expense))
    app.add_handler(CommandHandler("report", report))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
