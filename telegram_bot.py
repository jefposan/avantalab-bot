import csv
import os
import re
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackContext

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CSV_FILE = "dados.csv"

# ===== Utilitários =====
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
    Extrai todos os números do texto (00..99), converte para int
    e retorna uma lista de inteiros.
    """
    nums = re.findall(r"\d{1,2}", texto)
    dezenas = [int(n) for n in nums]
    return dezenas

def validar_dezenas(raw_text: str):
    dezenas = extrair_dezenas(raw_text)

    if len(dezenas) != 10:
        return False, "Você deve informar exatamente 10 dezenas (ex.: 1 6 12 23 30 34 41 45 52 60)."

    if any(d < 1 or d > 60 for d in dezenas):
        return False, "Todas as dezenas devem estar entre 01 e 60."

    if len(set(dezenas)) != 10:
        return False, "Não repita dezenas. Envie 10 números diferentes."

    # Ordenação numérica real
    dezenas_ordenadas = sorted(dezenas)
    return True, dezenas_ordenadas

def fmt(dezenas_int):
    return ", ".join(f"{d:02d}" for d in dezenas_int)

# ===== Fluxo =====
def pedir_dezenas(update: Update):
    update.message.reply_text(
        "🎟️ Obrigado pelo contato!\n"
        "Por favor, envie **10 dezenas** de 01 a 60, separadas por espaço (ex.: 1 6 12 23 30 34 41 45 52 60)."
    )

def start(update: Update, context: CallbackContext):
    # Sempre que /start for usado, entra no estado de aguardar dezenas
    context.user_data["aguardando_dezenas"] = True
    pedir_dezenas(update)

def handle(update: Update, context: CallbackContext):
    user = update.message.from_user
    username = user.username or user.first_name or str(user.id)
    text = update.message.text.strip()

    aguardando = context.user_data.get("aguardando_dezenas", None)

    # 1) Se acabou de encerrar uma aposta OU é a primeira interação: iniciar fluxo
    if aguardando is None or aguardando is False:
        context.user_data["aguardando_dezenas"] = True
        pedir_dezenas(update)
        return

    # 2) Se está aguardando dezenas, validar a mensagem atual
    valido, resultado = validar_dezenas(text)
    if not valido:
        update.message.reply_text(f"⚠️ {resultado}")
        return

    # 3) Confirmar, salvar e encerrar ciclo desta aposta
    dezenas_ordenadas = resultado  # já vem ordenado
    dezenas_fmt = fmt(dezenas_ordenadas)

    update.message.reply_text(
        f"Aposta registrada com sucesso! ✅\n"
        f"Suas dezenas em ordem crescente: {dezenas_fmt}"
    )
    salvar_csv(user.id, username, dezenas_fmt)

    # marca que a conversa foi concluída; próxima mensagem inicia novo ciclo
    context.user_data["aguardando_dezenas"] = False

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
