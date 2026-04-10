from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN ="8680588423:AAHjSd5TtCcw7bi8kDpq3lIgJX1lF6jw1Dw "

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salut 👋 botul funcționează")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot pornit...")
    app.run_polling()

if __name__ == "__main__":
    main()