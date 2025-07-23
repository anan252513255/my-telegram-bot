import json
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Lấy token từ biến môi trường
TOKEN = os.getenv("7980211121:AAHq9v27S5YMIowrVQJnhWcZqkF2zwNt_G0")

# File lưu dữ liệu
DATA_FILE = "data.json"

# Hàm xử lý /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! Bot đã chạy trên Render.")

# Hàm xử lý /add
def add(update: Update, context: CallbackContext):
    try:
        args = context.args
        if len(args) < 2:
            update.message.reply_text("❌ Sai cú pháp. Dùng: /add <số tiền> <nội dung>")
            return

        so_tien = int(args[0])
        noi_dung = " ".join(args[1:])
        user_id = str(update.message.from_user.id)
        ngay = datetime.now().strftime("%Y-%m-%d")

        # Đọc dữ liệu hiện có
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}

        # Ghi thêm chi tiêu
        if user_id not in data:
            data[user_id] = []

        data[user_id].append({
            "ngay": ngay,
            "so_tien": so_tien,
            "noi_dung": noi_dung
        })

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        update.message.reply_text(f"✅ Đã ghi {so_tien} cho: {noi_dung}")
    except Exception as e:
        update.message.reply_text("⚠️ Lỗi khi thêm chi tiêu.")
        print("Lỗi:", e)

def main():
    if not TOKEN:
        raise ValueError("❌ Chưa có TELEGRAM_TOKEN trong biến môi trường!")

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
