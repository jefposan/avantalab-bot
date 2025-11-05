import csv
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# Token do Bot vindo da variável de ambiente
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Nome do arquivo CSV
CSV_FILE = "dados.csv"


# === Garante que o arquivo CSV exista ===
def ensure_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "user_id", "username", "text"])


# === Salva a mensagem no CSV ===
def salvar_csv(user_id, username, texto):
    ensure_csv()
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [datetime.utcnow().isoformat(), user_id, username, texto])


# === Valida as dezenas enviadas ===
def validar_dezenas(texto):
    try:
        dezenas = [
            int(d) for d in texto.replace(",", " ").split() if d.isdigit()
        ]
        if len(dezenas) != 10:
            return False, "Você deve informar exatamente 10 dezenas."
        if len(set(dezenas)) != 10:
            return False, "Não repita dezenas."
        if any(d < 1 or d > 60 for d in dezenas):
            return False, "As dezenas devem estar entre 1 e 60."
        return True, dezenas
    except ValueError:
        return False, "Use apenas números separados por espaço ou vírgula."


# === Trata mensagens recebidas ===
def handle_message(update: Update, context: CallbackContext):
    msg = update.message
    texto = msg.text.strip()
    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name

    if texto.lower() in ["aposta", "jogar", "apostar", "quero apostar"]:
        update.message.reply_text(
            "🎟️ Obrigado pela aposta!\nPor favor, envie 10 dezenas de 01 a 60 separadas por espaço."
        )
        return

    valido, resultado = validar_dezenas(texto)
    if valido:
        # Ordena as dezenas numericamente
        resultado = sorted([int(d) for d in resultado])
        dezenas_formatadas = ", ".join(f"{d:02d}" for d in resultado)
        update.message.reply_text(
            f"Aposta registrada com sucesso! ✅\nSuas dezenas em ordem crescente: {dezenas_formatadas}"
        )
        salvar_csv(user_id, username, dezenas_formatadas)
    else:
        update.message.reply_text(f"⚠️ {resultado}")


# === Inicializa o bot ===
def main():
    ensure_csv()
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(
        MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
