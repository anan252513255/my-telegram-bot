import os
import json
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Cấu hình
TOKEN = os.getenv("TELEGRAM_TOKEN")
DATA_FILE = "data.json"

# Khởi tạo file dữ liệu nếu chưa có
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"transactions": []}, f)

# --- Hàm xử lý dữ liệu ---
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 **Bot Quản Lý Chi Tiêu**\n\n"
        "Các lệnh hỗ trợ:\n"
        "/add <số_tiền> <mô_tả> - Thêm chi tiêu\n"
        "/report - Xem tổng chi hôm nay\n"
        "/report <ngày> - Xem chi tiết theo ngày (VD: /report 2025-07-23)"
    )

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("⚠️ Sai cú pháp. Ví dụ: /add 50000 cơm trưa")
            return

        amount = float(args[0])
        description = " ".join(args[1:])
        today = datetime.now().strftime("%Y-%m-%d")

        data = load_data()
        data["transactions"].append({
            "date": today,
            "amount": amount,
            "description": description
        })
        save_data(data)

        await update.message.reply_text(
            f"✅ Đã thêm {amount:,.0f}đ cho: {description}\n"
            f"📅 Ngày: {today}"
        )

    except ValueError:
        await update.message.reply_text("⚠️ Số tiền phải là giá trị số!")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        date_filter = datetime.now().strftime("%Y-%m-%d") if not args else args[0]

        data = load_data()
        filtered = [t for t in data["transactions"] if t["date"] == date_filter]
        total = sum(t["amount"] for t in filtered)

        report_text = (
            f"📊 Báo cáo ngày {date_filter}\n"
            f"----------------------------\n"
            f"• Tổng chi: {total:,.0f}đ\n"
            f"• Số giao dịch: {len(filtered)}\n\n"
        )

        for idx, t in enumerate(filtered, 1):
            report_text += f"{idx}. {t['description']}: {t['amount']:,.0f}đ\n"

        await update.message.reply_text(report_text if filtered else "📌 Không có dữ liệu")

    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")

# --- Khởi chạy Bot ---
def main():
    app = Application.builder().token(TOKEN).build()
    
    # Đăng ký commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_expense))
    app.add_handler(CommandHandler("report", report))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
