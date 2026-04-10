import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salut 👋 botul funcționează")

def main():
    if not TOKEN:
        print("TOKEN lipsă!")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot pornit...")
    app.run_polling()

if __name__ == "__main__":
    main()
