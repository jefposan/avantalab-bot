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
            w.writerow(["timestamp_utc", "user_id", "username", "dezenas"])

def salvar_csv(user_id: int, username: str, dezenas_fmt: str):
    ensure_csv()
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([datetime.utcnow().isoformat(), user_id, username, dezenas_fmt])

def extrair_dezenas(texto: str):
    """
    Extrai números de 1 a 60 do texto e retorna como lista de inteiros.
    Aceita separações por espaço, vírgula etc.
    """
    nums = re.findall(r"\d{1,2}", texto)        # pega grupos de 1-2 dígitos
    dezenas = [int(n) for n in nums if 1 <= int(n) <= 60]
    return dezenas

def validar_dezenas(raw_text: str):
    dezenas = extrair_dezenas(raw_text)

    if len(dezenas) != 10:
        return False, "Você deve informar **exatamente 10** dezenas (ex.: 1 6 12 23 30 34 41 45 52 60)."

    if len(set(dezenas)) != 10:
        return False, "Não repita dezenas. Envie 10 números diferentes."

    # ordenação numérica real
    dezenas_ordenadas = sorted(dezenas)
    return True, dezenas_ordenadas

def fmt(dezenas_int):
    return ", ".join(f"{d:02d}" for d in dezenas_int)

# ============ mensagens ============
WELCOME = (
    "🎟️ Seja bem-vindo!\n"
    "Por favor, envie **10 dezenas** de 01 a 60 separadas por espaço "
    "(ex.: 1 6 12 23 30 34 41 45 52 60)."
)

def pedir_dezenas(update: Update):
    update.message.reply_text(WELCOME)

# ============ fluxos ============
def start(update: Update, context: CallbackContext):
    # sempre inicia (ou reinicia) o ciclo
    context.user_data["fase"] = "aguardando_dezenas"
    pedir_dezenas(update)

def handle_text(update: Update, context: CallbackContext):
    user = update.message.from_user
    username = user.username or user.first_name or str(user.id)
    text = update.message.text.strip()

    fase = context.user_data.get("fase")

    # 1) primeira interação OU conversa recém finalizada -> mostra boas-vindas e entra em "aguardando_dezenas"
    if fase is None or fase == "finalizado":
        context.user_data["fase"] = "aguardando_dezenas"
        pedir_dezenas(update)
        return

    # 2) aguardando as dezenas -> valida
    if fase == "aguardando_dezenas":
        ok, resultado = validar_dezenas(text)
        if not ok:
            update.message.reply_text(f"⚠️ {resultado}")
            return

        dezenas_fmt = fmt(resultado)  # já ordenado
        update.message.reply_text(
            f"Aposta registrada com sucesso! ✅\n"
            f"Suas dezenas em ordem crescente: {dezenas_fmt}"
        )
        salvar_csv(user.id, username, dezenas_fmt)

        # encerra ciclo; próxima mensagem recomeça com boas-vindas
        context.user_data["fase"] = "finalizado"
        return

    # 3) fallback seguro
    context.user_data["fase"] = "aguardando_dezenas"
    pedir_dezenas(update)

def main():
    ensure_csv()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    # permite que "começar" também reinicie o fluxo
    dp.add_handler(MessageHandler(Filters.regex(r"(?i)^\s*começar\s*$"), start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
