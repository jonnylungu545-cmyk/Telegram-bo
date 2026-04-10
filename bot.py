import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")

# 🔘 MENIU
menu = ReplyKeyboardMarkup(
    [
        ["📦 Produse", "💰 Prețuri"],
        ["📞 Contact", "ℹ️ Info"]
    ],
    resize_keyboard=True
)

ADMIN_ID = 123456789  # 👈 pune ID-ul tău Telegram aici

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salut! Bine ai venit la botul meu",
        reply_markup=menu
    )

# mesaje
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📦 Produse":
        await update.message.reply_text(
            "📦 Servicii disponibile:\n"
            "- Crypto exchange\n"
            "- Servicii digitale\n"
            "- Consultanță"
        )

    elif text == "💰 Prețuri":
        await update.message.reply_text(
            "💰 Prețuri:\n"
            "- Depinde de volum\n"
            "- Scrie-mi pentru ofertă"
        )

    elif text == "📞 Contact":
        await update.message.reply_text(
            "📞 Contact admin:\n@username_tau"
        )

    elif text == "ℹ️ Info":
        await update.message.reply_text(
            "ℹ️ Acest bot este creat pentru servicii rapide și automatizare."
        )

    else:
        await update.message.reply_text("Alege o opțiune din meniu 👇")

# admin
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Nu ai acces")
        return

    await update.message.reply_text("🔐 Admin panel activ")

# main
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot pornit...")
    app.run_polling()

if __name__ == "__main__":
    main()
