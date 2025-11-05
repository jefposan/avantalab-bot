import csv
import os
import re
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackContext

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CSV_FILE = "dados.csv"


# ===== utilitários =====
def ensure_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["timestamp_utc", "user_id", "username", "dezenas"])


def salvar_csv(user_id: int, username: str, dezenas_fmt: str):
    ensure_csv()
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [datetime.utcnow().isoformat(), user_id, username, dezenas_fmt])


def extrair_dezenas(texto: str):
    """Extrai todos os números de 1 a 60 do texto"""
    return [int(n) for n in re.findall(r"\d{1,2}", texto) if 1 <= int(n) <= 60]


def validar_dezenas(raw_text: str):
    dezenas = extrair_dezenas(raw_text)
    if len(dezenas) != 10:
        return False, "Você deve informar exatamente 10 dezenas (ex.: 1 6 12 23 30 34 41 45 52 60)."
    if len(set(dezenas)) != 10:
        return False, "Não repita dezenas. Envie 10 números diferentes."
    dezenas_ordenadas = sorted(dezenas)
    return True, dezenas_ordenadas


def fmt(dezenas_int):
    return ", ".join(f"{d:02d}" for d in dezenas_int)


# ===== mensagens =====
def pedir_dezenas(update: Update):
    update.message.reply_text(
        "🎟️ Obrigado pelo contato!\n"
        "Por favor, envie **10 dezenas** de 01 a 60, separadas por espaço (ex.: 1 6 12 23 30 34 41 45 52 60)."
    )


def start(update: Update, context: CallbackContext):
    context.user_data["fase"] = "aguardando_dezenas"
    pedir_dezenas(update)


def handle(update: Update, context: CallbackContext):
    user = update.message.from_user
    username = user.username or user.first_name or str(user.id)
    text = update.message.text.strip()

    fase = context.user_data.get("fase")

    # 1️⃣ Se é o primeiro contato ou acabou uma aposta anterior → inicia o fluxo
    if fase is None or fase == "finalizado":
        context.user_data["fase"] = "aguardando_dezenas"
        pedir_dezenas(update)
        return

    # 2️⃣ Se está aguardando dezenas, faz a validação
    if fase == "aguardando_dezenas":
        valido, resultado = validar_dezenas(text)
        if not valido:
            update.message.reply_text(f"⚠️ {resultado}")
            return

        dezenas_fmt = fmt(resultado)
        update.message.reply_text(
            f"Aposta registrada com sucesso! ✅\n"
            f"Suas dezenas em ordem crescente: {dezenas_fmt}")
        salvar_csv(user.id, username, dezenas_fmt)
        context.user_data["fase"] = "finalizado"
        return

    # 3️⃣ fallback (caso raro)
    pedir_dezenas(update)
    context.user_data["fase"] = "aguardando_dezenas"


def main():
    ensure_csv()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
