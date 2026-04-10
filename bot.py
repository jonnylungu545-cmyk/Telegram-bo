import os
import json
import requests
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

DB_FILE = "payments.json"

user_lang = {}
user_step = {}

USD_TO_LEI = 20.50
COMMISSION = 1.01


# 💱 LIVE CRYPTO
def get_crypto_rates():
    try:
        btc = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT").json()
        ltc = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=LTCUSDT").json()

        return {
            "BTC": float(btc["price"]),
            "LTC": float(ltc["price"])
        }
    except:
        return {"BTC": 42000, "LTC": 70}


# 💾 DB
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)


# 🔘 MENIU
lang_menu = ReplyKeyboardMarkup(
    [["🇷🇴 Română", "🇷🇺 Русский"]],
    resize_keyboard=True
)

menu_ro = ReplyKeyboardMarkup(
    [["💳 Plată", "📜 Istoric", "📊 Dashboard"]],
    resize_keyboard=True
)


# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🚀 START", callback_data="start_btn")]]

    await update.message.reply_text(
        "🌍 Apasă START",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# 🔘 CALLBACK
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id

    if q.data == "start_btn":
        await q.edit_message_text("✔ Alege limba:", reply_markup=lang_menu)

    elif q.data == "crypto_btc":
        user_step[user_id] = "BTC"
        await q.edit_message_text("✍ Introdu suma BTC")

    elif q.data == "crypto_ltc":
        user_step[user_id] = "LTC"
        await q.edit_message_text("✍ Introdu suma LTC")


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


# 📊 DASHBOARD
async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    db = load_db()

    users = len(db)
    total = sum(len(v) for v in db.values())

    await update.message.reply_text(
        f"📊 DASHBOARD\n\n👤 Users: {users}\n💰 Plăți: {total}"
    )


# 📜 ISTORIC
async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    uid = str(update.message.from_user.id)

    data = db.get(uid, [])

    if not data:
        await update.message.reply_text("📭 Fără plăți")
        return

    msg = "📜 Istoric:\n\n"

    for p in data[-10:]:
        msg += f"{p['amount']} {p['crypto']} → {p['lei']:.2f} MDL\n"

    await update.message.reply_text(msg)


# 💬 MESSAGE HANDLER
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # limbă
    if text == "🇷🇴 Română":
        user_lang[user_id] = "ro"
        await update.message.reply_text("✔ Română", reply_markup=menu_ro)
        return

    # 🔥 CRYPTO INPUT
    if user_id in user_step:
        try:
            amount = float(text)
        except:
            await update.message.reply_text("❌ Sumă invalidă")
            return

        crypto = user_step[user_id]

        rates = get_crypto_rates()
        price = rates[crypto]

        usd = amount * price
        lei = usd * USD_TO_LEI * COMMISSION

        db = load_db()
        uid = str(user_id)

        if uid not in db:
            db[uid] = []

        db[uid].append({
            "crypto": crypto,
            "amount": amount,
            "usd": usd,
            "lei": lei
        })

        save_db(db)

        user_step.pop(user_id)

        await update.message.reply_text(
            f"💰 Conversie:\n"
            f"{amount} {crypto}\n"
            f"{usd:.2f} USD\n"
            f"{lei:.2f} MDL\n\n"
            "⏳ Verificare 5-10 min"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💰 CRYPTO\n{amount} {crypto}\n≈ {lei:.2f} MDL\nUser: {user_id}"
        )
        return


# 🚀 MAIN
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dashboard", dashboard))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot pornit...")
    app.run_polling()


if __name__ == "__main__":
    main()
