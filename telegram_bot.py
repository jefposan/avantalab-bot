import csv
import os
import re
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackContext

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CSV_FILE = "dados.csv"


# ============ utilitários ============
def ensure_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                "timestamp_utc", "user_id", "username", "nome_apostador",
                "dezenas"
            ])


def salvar_csv(user_id: int, username: str, nome_apostador: str,
               dezenas_fmt: str):
    ensure_csv()
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            datetime.utcnow().isoformat(), user_id, username, nome_apostador,
            dezenas_fmt
        ])


def extrair_dezenas(texto: str):
    nums = re.findall(r"\d{1,2}", texto)
    dezenas = [int(n) for n in nums if 1 <= int(n) <= 60]
    return dezenas


def validar_dezenas(raw_text: str):
    dezenas = extrair_dezenas(raw_text)

    if len(dezenas) != 10:
        return False, "Você deve informar **exatamente 10** dezenas (ex.: 1 6 12 23 30 34 41 45 52 60)."

    if len(set(dezenas)) != 10:
        return False, "Não repita dezenas. Envie 10 números diferentes."

    dezenas_ordenadas = sorted(dezenas)
    return True, dezenas_ordenadas


def fmt(dezenas_int):
    return ", ".join(f"{d:02d}" for d in dezenas_int)


# ============ mensagens ============
WELCOME = ("🎟️ Seja bem-vindo!\n"
           "Por favor, envie **10 dezenas** de 01 a 60 separadas por espaço "
           "(ex.: 1 6 12 23 30 34 41 45 52 60).")


def pedir_dezenas(update: Update):
    update.message.reply_text(WELCOME)


# ============ fluxos ============
def start(update: Update, context: CallbackContext):
    context.user_data.clear()
    context.user_data["fase"] = "aguardando_dezenas"
    pedir_dezenas(update)


def handle_text(update: Update, context: CallbackContext):
    user = update.message.from_user
    username = user.username or user.first_name or str(user.id)
    text = update.message.text.strip()
    fase = context.user_data.get("fase")

    # 1) início ou reinício
    if fase is None or fase == "finalizado":
        context.user_data["fase"] = "aguardando_dezenas"
        pedir_dezenas(update)
        return

    # 2) aguardando dezenas
    if fase == "aguardando_dezenas":
        ok, resultado = validar_dezenas(text)
        if not ok:
            update.message.reply_text(f"⚠️ {resultado}")
            return

        dezenas_fmt = fmt(resultado)
        context.user_data["dezenas_fmt"] = dezenas_fmt
        update.message.reply_text(
            f"Aposta registrada com sucesso! ✅\n"
            f"Suas dezenas em ordem crescente: {dezenas_fmt}\n\n"
            f"Agora, por favor, envie o **nome do apostador** para finalizar o registro."
        )
        context.user_data["fase"] = "aguardando_nome"
        return

    # 3) aguardando nome do apostador
    if fase == "aguardando_nome":
        nome_apostador = text.strip().title()
        dezenas_fmt = context.user_data.get("dezenas_fmt", "")
        salvar_csv(user.id, username, nome_apostador, dezenas_fmt)
        update.message.reply_text(f"✅ Aposta finalizada com sucesso!\n"
                                  f"Nome do apostador: {nome_apostador}\n"
                                  f"Dezenas: {dezenas_fmt}\n\n"
                                  f"Boa sorte! 🍀")
        context.user_data["fase"] = "finalizado"
        context.user_data.pop("dezenas_fmt", None)
        return

    # 4) fallback
    context.user_data["fase"] = "aguardando_dezenas"
    pedir_dezenas(update)


def main():
    ensure_csv()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.regex(r"(?i)^\s*começar\s*$"),
                                  start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command,
                                  handle_text))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
