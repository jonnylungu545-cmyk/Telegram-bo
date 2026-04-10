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
user_step = {}
payments_history = {}

# 💰 CONFIG
MIA_PHONE = "067268243"
BPAY_ACCOUNT = "11582218"

BTC_RATE = 42000
LTC_RATE = 70
USD_TO_LEI = 20.50
COMMISSION = 1.01

# 🔘 LIMBĂ
lang_menu = ReplyKeyboardMarkup(
    [["🇷🇴 Română", "🇷🇺 Русский"]],
    resize_keyboard=True
)

menu_ro = ReplyKeyboardMarkup(
    [
        ["📦 Produse", "💰 Prețuri"],
        ["📞 Contact", "ℹ️ Info"],
        ["💳 Plată"],
        ["🔐 Admin"]
    ],
    resize_keyboard=True
)

menu_ru = ReplyKeyboardMarkup(
    [
        ["📦 Товары", "💰 Цены"],
        ["📞 Контакты", "ℹ️ Инфо"],
        ["💳 Оплата"],
        ["🔐 Админ"]
    ],
    resize_keyboard=True
)

# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.message.from_user.id)

    keyboard = [[InlineKeyboardButton("🚀 START", callback_data="start_btn")]]
    await update.message.reply_text(
        "🌍 Apasă START",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 🔘 CALLBACK
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "start_btn":
        await query.edit_message_text("✔ Alege limba:", reply_markup=lang_menu)

    elif query.data == "crypto_btc":
        user_step[user_id] = "BTC"
        await query.edit_message_text("✍ Introdu suma BTC (ex: 0.01)")

    elif query.data == "crypto_ltc":
        user_step[user_id] = "LTC"
        await query.edit_message_text("✍ Introdu suma LTC (ex: 1.5)")

    elif query.data.startswith("pay_"):
        await query.edit_message_text(
            "⏳ Plata înregistrată\nVerificare 5-10 min"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💰 PLATĂ\nUser: {user_id}"
        )

# 💳 PLĂȚI
async def payments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("₿ BTC", callback_data="crypto_btc"),
            InlineKeyboardButton("Ł LTC", callback_data="crypto_ltc")
        ]
    ]

    await update.message.reply_text(
        "💳 Alege crypto:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 💬 MESSAGE HANDLER
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # limbă
    if text == "🇷🇴 Română":
        user_lang[user_id] = "ro"
        await update.message.reply_text("✔ Română", reply_markup=menu_ro)
        return

    if text == "🇷🇺 Русский":
        user_lang[user_id] = "ru"
        await update.message.reply_text("✔ Русский", reply_markup=menu_ru)
        return

    # 🔥 CRYPTO INPUT
    if user_id in user_step:
        try:
            amount = float(text)
        except:
            await update.message.reply_text("❌ Sumă invalidă")
            return

        crypto = user_step[user_id]

        rate = BTC_RATE if crypto == "BTC" else LTC_RATE

        usd = amount * rate
        lei = usd * USD_TO_LEI * COMMISSION

        payments_history.setdefault(user_id, []).append({
            "crypto": crypto,
            "amount": amount,
            "usd": usd,
            "lei": lei
        })

        user_step.pop(user_id)

        await update.message.reply_text(
            f"💰 Conversie:\n"
            f"{amount} {crypto}\n"
            f"{usd:.2f} USD\n"
            f"{lei:.2f} MDL (cu 1% comision)\n\n"
            "⏳ Verificare 5-10 min"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💰 CRYPTO\n{amount} {crypto}\n≈ {lei:.2f} MDL"
        )
        return

    lang = user_lang.get(user_id, "ro")

    if lang == "ro":
        if text == "💳 Plată":
            await payments(update, context)

# 🚀 MAIN
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot pornit...")
    app.run_polling()

if __name__ == "__main__":
    main()
