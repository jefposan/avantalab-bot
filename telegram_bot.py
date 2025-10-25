import csv
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Token vem de variável de ambiente
CSV_FILE = "dados.csv"

def ensure_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "user_id", "username", "text"])

def handle_message(update: Update, context: CallbackContext):
    msg = update.message
    ts = datetime.utcnow().isoformat()
    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.full_name
    text = msg.text or ""
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([ts, user_id, username, text])

def main():
    ensure_csv()
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text | Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
