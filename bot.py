import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler
)

TOKEN = os.getenv("TOKEN")
ADMIN_ID = 8777102322

users = set()
user_lang = {}

# 💰 CONFIG PLĂȚI
MIA_PHONE = "067268243"
BPAY_ACCOUNT = "11582218"

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
        ["💳 Plată"],
        ["🔐 Admin"]
    ],
    resize_keyboard=True
)

# 🔘 MENIU RU
menu_ru = ReplyKeyboardMarkup(
    [
        ["📦 Товары", "💰 Цены"],
        ["📞 Контакты", "ℹ️ Инфо"],
        ["💳 Оплата"],
        ["🔐 Админ"]
    ],
    resize_keyboard=True
)

# 🚀 START CU BUTON
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    users.add(user_id)

    keyboard = [
        [InlineKeyboardButton("🚀 START", callback_data="start_btn")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🌍 Apasă START pentru a continua",
        reply_markup=reply_markup
    )

# 🔘 BUTON HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start_btn":
        await query.edit_message_text(
            "✔ Bot activ!\n🌍 Alege limba:",
            reply_markup=lang_menu
        )

    elif query.data.startswith("pay_"):
        user_id = query.from_user.id

        await query.edit_message_text(
            "⏳ Plata a fost înregistrată!\n"
            "⏱ Verificare în 5-10 minute...\n\n"
            "✔ Vei primi confirmare după verificare."
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💰 PLATĂ NOUĂ!\nUser ID: {user_id}\nVerifică plata manual."
        )

# 🔐 ADMIN
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Acces interzis")
        return

    await update.message.reply_text(
        "🔐 ADMIN PANEL\nComenzi:\n/broadcast mesaj"
    )

# 📢 BROADCAST
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

    await update.message.reply_text(f"✔ Trimise la {sent} utilizatori")

# 💳 PLĂȚI
async def payments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    keyboard = [
        [InlineKeyboardButton("✅ Am efectuat plata", callback_data=f"pay_{user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "💳 Metode de plată:\n\n"
        f"📱 MIA Transfer: {MIA_PHONE}\n"
        f"🏧 Paynet: {MIA_PHONE}\n"
        f"🏦 RunPay: {MIA_PHONE}\n"
        f"💠 Bpay Account: {BPAY_ACCOUNT}\n\n"
        "💡 După plată apasă butonul de mai jos."
    )

    await update.message.reply_text(text, reply_markup=reply_markup)

# 💬 HANDLER PRINCIPAL
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # limbă
    if text == "🇷🇴 Română":
        user_lang[user_id] = "ro"
        await update.message.reply_text("✔ Limba: Română", reply_markup=menu_ro)
        return

    if text == "🇷🇺 Русский":
        user_lang[user_id] = "ru"
        await update.message.reply_text("✔ Язык: Русский", reply_markup=menu_ru)
        return

    lang = user_lang.get(user_id, "ro")

    if lang == "ro":
        if text == "📦 Produse":
            await update.message.reply_text("📦 Servicii: crypto, digital, consultanță")
        elif text == "💰 Prețuri":
            await update.message.reply_text("💰 Prețuri personalizate")
        elif text == "📞 Contact":
            await update.message.reply_text("📞 Contact: @username")
        elif text == "ℹ️ Info":
            await update.message.reply_text("ℹ️ Bot automat servicii")
        elif text == "💳 Plată":
            await payments(update, context)
        elif text == "🔐 Admin":
            await admin(update, context)
        else:
            await update.message.reply_text("Alege din meniu 👇")

    else:
        if text == "📦 Товары":
            await update.message.reply_text("📦 Услуги: крипто, цифровые, консультации")
        elif text == "💰 Цены":
            await update.message.reply_text("💰 Цены индивидуальные")
        elif text == "📞 Контакты":
            await update.message.reply_text("📞 Контакт: @username")
        elif text == "ℹ️ Инфо":
            await update.message.reply_text("ℹ️ Авто бот услуг")
        elif text == "💳 Оплата":
            await payments(update, context)
        elif text == "🔐 Админ":
            await admin(update, context)
        else:
            await update.message.reply_text("Выберите из меню 👇")

# 🚀 MAIN
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot pornit...")
    app.run_polling()

if __name__ == "__main__":
    main()
