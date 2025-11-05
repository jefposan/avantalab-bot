import csv
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CSV_FILE = "dados.csv"


# === Garante que o arquivo CSV existe ===
def ensure_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "user_id", "username", "text"])


# === Valida as dezenas enviadas ===
def validar_dezenas(texto):
    try:
        dezenas = list(map(int, texto.replace(",", " ").split()))
        if len(dezenas) != 10:
            return False, "Você precisa enviar exatamente 10 dezenas."
        if len(set(dezenas)) != 10:
            return False, "Não repita números. Todos devem ser diferentes."
        if any(d < 1 or d > 60 for d in dezenas):
            return False, "Todos os números devem estar entre 1 e 60."
        return True, dezenas
    except ValueError:
        return False, "Envie apenas números separados por espaço (ex: 5 12 23 ...)."


# === Armazena dados no CSV ===
def salvar_csv(user_id, username, texto):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), user_id, username, texto])


# === Quando o usuário envia mensagem ===
def handle_message(update: Update, context: CallbackContext):
    msg = update.message.text.strip()
    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name

    # Verifica se a pessoa está iniciando uma aposta
    if "apost" in msg.lower():  # ex: "quero apostar"
        update.message.reply_text(
            "Obrigado pela aposta! 🎟️\nPor favor, envie 10 dezenas de 01 a 60 separadas por espaço."
        )
        salvar_csv(user_id, username, msg)
        return

    # Se enviou dezenas, valida
    valido, resultado = validar_dezenas(msg)
    if valido:
        dezenas_formatadas = ", ".join(f"{d:02d}" for d in resultado)
        update.message.reply_text(
            f"Aposta registrada com sucesso! ✅\nSuas dezenas: {dezenas_formatadas}"
        )
        salvar_csv(user_id, username, dezenas_formatadas)
    else:
        update.message.reply_text(f"❌ {resultado}")


# === Inicializa o bot ===
def main():
    ensure_csv()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(
        MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
