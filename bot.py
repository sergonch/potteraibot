import logging
import os
import re

import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 @potteraibot готов!\nГруппа: @potteraibot [вопрос]"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""

    # Молчим в группе, если нет упоминания
    if update.effective_chat.type != "private" and not re.search(
        r"@potteraibot", text, re.IGNORECASE
    ):
        return

    # Убираем @potteraibot
    query = re.sub(r"@potteraibot\s*", "", text, flags=re.IGNORECASE).strip()

    try:
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "sonar",
            "messages": [{"role": "user", "content": query}],
        }

        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        data = resp.json()

        if resp.status_code == 200 and data.get("choices"):
            answer = data["choices"][0]["message"]["content"]
        else:
            answer = f"❌ API: {data}"

        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(f"❌ {str(e)}")


def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN не задан в переменных окружения")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 @potteraibot запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()
