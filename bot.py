import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")
ADMIN_ID = 8777102322

users = set()
user_lang = {}

# 🔘 MENIU LIMBĂ
lang_menu = ReplyKeyboardMarkup(
    [["🇷🇴 Română", "🇷🇺 Русский"]],
    resize_keyboard=True
)

# 🔘 MENIU RO
menu_ro = ReplyKeyboardMarkup(
    [
        ["📦 Produse", "💰 Prețuri"],
        ["📞 Contact", "ℹ️ Info"],
        ["🔐 Admin"]
    ],
    resize_keyboard=True
)

# 🔘 MENIU RU
menu_ru = ReplyKeyboardMarkup(
    [
        ["📦 Товары", "💰 Цены"],
        ["📞 Контакты", "ℹ️ Инфо"],
        ["🔐 Админ"]
    ],
    resize_keyboard=True
)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    users.add(user_id)

    await update.message.reply_text(
        "🌍 Alege limba / Выберите язык:",
        reply_markup=lang_menu
    )

# ADMIN PANEL
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Acces interzis")
        return

    await update.message.reply_text(
        "🔐 ADMIN PANEL\n"
        "Comenzi disponibile:\n"
        "/broadcast mesaj"
    )

# BROADCAST
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    msg = " ".join(context.args)

    if not msg:
        await update.message.reply_text("Scrie: /broadcast mesaj")
        return

    sent = 0

    for user in users:
        try:
            await context.bot.send_message(chat_id=user, text="📢 " + msg)
            sent += 1
        except:
            pass

    await update.message.reply_text(f"✔ Trimis la {sent} utilizatori")

# HANDLER PRINCIPAL
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # alegere limbă
    if text == "🇷🇴 Română":
        user_lang[user_id] = "ro"
        await update.message.reply_text("✔ Limba: Română", reply_markup=menu_ro)
        return

    if text == "🇷🇺 Русский":
        user_lang[user_id] = "ru"
        await update.message.reply_text("✔ Язык: Русский", reply_markup=menu_ru)
        return

    lang = user_lang.get(user_id, "ro")

    # ROMÂNĂ
    if lang == "ro":
        if text == "📦 Produse":
            await update.message.reply_text("📦 Servicii: crypto, digital, consultanță")
        elif text == "💰 Prețuri":
            await update.message.reply_text("💰 Prețuri personalizate")
        elif text == "📞 Contact":
            await update.message.reply_text("📞 Contact: @username")
        elif text == "ℹ️ Info":
            await update.message.reply_text("ℹ️ Bot automat servicii")
        elif text == "🔐 Admin":
            await admin(update, context)
        else:
            await update.message.reply_text("Alege din meniu 👇")

    # RUSĂ
    else:
        if text == "📦 Товары":
            await update.message.reply_text("📦 Услуги: крипто, цифровые, консультации")
        elif text == "💰 Цены":
            await update.message.reply_text("💰 Цены индивидуальные")
        elif text == "📞 Контакты":
            await update.message.reply_text("📞 Контакт: @username")
        elif text == "ℹ️ Инфо":
            await update.message.reply_text("ℹ️ Авто бот услуг")
        elif text == "🔐 Админ":
            await admin(update, context)
        else:
            await update.message.reply_text("Выберите из меню 👇")

# MAIN + HANDLERS
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot pornit...")
    app.run_polling()

if __name__ == "__main__":
    main()
