import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")

# stocare limbă simplă în memorie
user_lang = {}

# 🔘 Meniu RO
menu_ro = ReplyKeyboardMarkup(
    [
        ["📦 Produse", "💰 Prețuri"],
        ["📞 Contact", "ℹ️ Info"]
    ],
    resize_keyboard=True
)

# 🔘 Meniu RU
menu_ru = ReplyKeyboardMarkup(
    [
        ["📦 Товары", "💰 Цены"],
        ["📞 Контакты", "ℹ️ Инфо"]
    ],
    resize_keyboard=True
)

# /start - alegere limbă
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(
        [["🇷🇴 Română", "🇷🇺 Русский"]],
        resize_keyboard=True
    )

    await update.message.reply_text(
        "🌍 Alege limba / Выберите язык:",
        reply_markup=keyboard
    )

# handler principal
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # 🌍 alegere limbă
    if text == "🇷🇴 Română":
        user_lang[user_id] = "ro"
        await update.message.reply_text("✔ Limba selectată: Română", reply_markup=menu_ro)
        return

    if text == "🇷🇺 Русский":
        user_lang[user_id] = "ru"
        await update.message.reply_text("✔ Выбран язык: Русский", reply_markup=menu_ru)
        return

    lang = user_lang.get(user_id, "ro")

    # 🇷🇴 ROMÂNĂ
    if lang == "ro":
        if text == "📦 Produse":
            await update.message.reply_text("📦 Servicii: crypto, digital, consultanță")
        elif text == "💰 Prețuri":
            await update.message.reply_text("💰 Prețuri în funcție de serviciu")
        elif text == "📞 Contact":
            await update.message.reply_text("📞 Contact: @username_tau")
        elif text == "ℹ️ Info":
            await update.message.reply_text("ℹ️ Bot automat pentru servicii")
        else:
            await update.message.reply_text("Alege o opțiune din meniu 👇")

    # 🇷🇺 RUSĂ
    else:
        if text == "📦 Товары":
            await update.message.reply_text("📦 Услуги: крипто, цифровые, консультации")
        elif text == "💰 Цены":
            await update.message.reply_text("💰 Цены зависят от услуги")
        elif text == "📞 Контакты":
            await update.message.reply_text("📞 Контакт: @username")
        elif text == "ℹ️ Инфо":
            await update.message.reply_text("ℹ️ Автоматический бот услуг")
        else:
            await update.message.reply_text("Выберите опцию из меню 👇")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot pornit...")
    app.run_polling()

if __name__ == "__main__":
    main()
