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
user_data_temp = {}

USD_TO_LEI = 20.50
COMMISSION = 1.01

MIA_PHONE = "067268243"
BPAY_ACCOUNT = "11582218"


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
    [["💳 Schimb Crypto", "📜 Istoric"]],
    resize_keyboard=True
)


# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🚀 START", callback_data="start_btn")]]

    await update.message.reply_text(
        "🔥 Bun venit!\nApasă START",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# 🔘 CALLBACK
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id

    if q.data == "start_btn":
        await q.message.reply_text("🌍 Alege limba:", reply_markup=lang_menu)

    elif q.data == "btc":
        user_step[user_id] = "WAIT_ADDRESS"
        user_data_temp[user_id] = {"crypto": "BTC"}
        await q.message.reply_text(
            "📩 Trimite:\n\n- adresă BTC sau QR\n- suma dorită (ex: 0.01)"
        )

    elif q.data == "ltc":
        user_step[user_id] = "WAIT_ADDRESS"
        user_data_temp[user_id] = {"crypto": "LTC"}
        await q.message.reply_text(
            "📩 Trimite:\n\n- adresă LTC sau QR\n- suma dorită (ex: 0.5)"
        )

    elif q.data == "confirm_pay":
        data = user_data_temp.get(user_id)

        await q.message.reply_text(
            "⏳ Plata în verificare (5-10 min)"
        )

        # 🔔 notificare admin
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"💰 COMANDĂ NOUĂ\n\n"
                f"User: {user_id}\n"
                f"{data['amount']} {data['crypto']}\n"
                f"≈ {data['lei']:.2f} MDL\n\n"
                f"Adresă:\n{data['address']}"
            )
        )

    elif q.data.startswith("done_"):
        target_user = int(q.data.split("_")[1])

        await context.bot.send_message(
            chat_id=target_user,
            text="✅ Transfer trimis! Verifică wallet-ul."
        )

        await q.message.edit_text("✅ Finalizat")


# 💳 START PLATĂ
async def payments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("₿ BTC", callback_data="btc"),
            InlineKeyboardButton("Ł LTC", callback_data="ltc")
        ]
    ]

    await update.message.reply_text(
        "💳 Alege criptomoneda:",
        reply_markup=InlineKeyboardMarkup(keyboard)
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


# 💬 HANDLER
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # limbă
    if text == "🇷🇴 Română":
        user_lang[user_id] = "ro"
        await update.message.reply_text("✔ Română", reply_markup=menu_ro)
        return

    # meniu
    if text == "💳 Schimb Crypto":
        await payments(update, context)
        return

    if text == "📜 Istoric":
        await history(update, context)
        return

    # 🔥 PAS 1: ADRESĂ + SUMĂ
    if user_step.get(user_id) == "WAIT_ADDRESS":
        try:
            parts = text.split()
            address = parts[0]
            amount = float(parts[1])
        except:
            await update.message.reply_text(
                "❌ Format greșit\nEx: LTC_ADRESA 0.5"
            )
            return

        crypto = user_data_temp[user_id]["crypto"]

        rates = get_crypto_rates()
        usd = amount * rates[crypto]
        lei = usd * USD_TO_LEI * COMMISSION

        user_data_temp[user_id].update({
            "address": address,
            "amount": amount,
            "lei": lei
        })

        keyboard = [
            [InlineKeyboardButton("✅ Am plătit", callback_data="confirm_pay")]
        ]

        await update.message.reply_text(
            f"💰 Vei primi:\n{amount} {crypto}\n\n"
            f"💵 De plătit: {lei:.2f} MDL\n\n"
            f"📱 MIA: {MIA_PHONE}\n"
            f"🏦 Bpay: {BPAY_ACCOUNT}\n\n"
            "👇 După plată apasă:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        user_step.pop(user_id)

        # salvare DB
        db = load_db()
        uid = str(user_id)

        if uid not in db:
            db[uid] = []

        db[uid].append(user_data_temp[user_id])
        save_db(db)


# 🚀 MAIN
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🔥 BOT EXCHANGE LIVE")
    app.run_polling()


if __name__ == "__main__":
    main()
