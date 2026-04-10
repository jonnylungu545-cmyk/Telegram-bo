import os
import json
import requests
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler

TOKEN = os.getenv("TOKEN")
ADMIN_ID = 8777102322

DB_FILE = "payments.json"

user_lang = {}
user_step = {}

USD_TO_LEI = 20.50
COMMISSION = 1.01

# 💳 DATE PLATĂ
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
    [
        ["💳 Plată", "📜 Istoric"],
        ["📊 Dashboard", "💱 Calculator"]
    ],
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
    data = q.data

    if data == "start_btn":
        await q.message.reply_text("🌍 Alege limba:", reply_markup=lang_menu)

    elif data == "crypto_btc":
        user_step[user_id] = "BTC"
        await q.message.reply_text("✍ Introdu suma BTC")

    elif data == "crypto_ltc":
        user_step[user_id] = "LTC"
        await q.message.reply_text("✍ Introdu suma LTC")

    elif data == "paid":
        await q.message.reply_text(
            "✅ Plata a fost trimisă!\n⏳ Se verifică în 5-10 minute"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💰 CONFIRMARE PLATĂ\nUser: {user_id}"
        )


# 💳 PLĂȚI
async def payments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rates = get_crypto_rates()

    keyboard = [
        [
            InlineKeyboardButton("₿ BTC", callback_data="crypto_btc"),
            InlineKeyboardButton("Ł LTC", callback_data="crypto_ltc")
        ],
        [InlineKeyboardButton("✅ Am plătit", callback_data="paid")]
    ]

    await update.message.reply_text(
        f"💳 Metode de plată:\n\n"
        f"📱 MIA Transfer: {MIA_PHONE}\n"
        f"🏧 Paynet: {MIA_PHONE}\n"
        f"🏦 RunPay: {MIA_PHONE}\n"
        f"💠 Bpay: {BPAY_ACCOUNT}\n\n"
        f"📊 Curs live:\n"
        f"BTC: {rates['BTC']:.2f}$\n"
        f"LTC: {rates['LTC']:.2f}$\n\n"
        "👇 Alege crypto sau confirmă plata:",
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


# 💱 CALCULATOR
async def calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_step[update.message.from_user.id] = "CALC"
    await update.message.reply_text("✍ Introdu suma în USD")


# 💬 MESSAGE HANDLER
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if text == "🇷🇴 Română":
        user_lang[user_id] = "ro"
        await update.message.reply_text("✔ Română", reply_markup=menu_ro)
        return

    # calculator
    if user_step.get(user_id) == "CALC":
        try:
            usd = float(text)
        except:
            await update.message.reply_text("❌ Număr invalid")
            return

        lei = usd * USD_TO_LEI
        await update.message.reply_text(f"💱 {usd}$ = {lei:.2f} MDL")

        user_step.pop(user_id)
        return

    # crypto
    if user_id in user_step:
        try:
            amount = float(text)
        except:
            await update.message.reply_text("❌ Sumă invalidă")
            return

        crypto = user_step[user_id]
        rates = get_crypto_rates()

        usd = amount * rates[crypto]
        lei = usd * USD_TO_LEI * COMMISSION

        db = load_db()
        uid = str(user_id)

        db.setdefault(uid, []).append({
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
            f"{usd:.2f}$\n"
            f"{lei:.2f} MDL\n\n"
            "⏳ Așteaptă confirmarea"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💰 CRYPTO\n{amount} {crypto}\n≈ {lei:.2f} MDL\nUser: {user_id}"
        )
        return

    # meniu
    if text == "💳 Plată":
        await payments(update, context)

    elif text == "📜 Istoric":
        await history(update, context)

    elif text == "📊 Dashboard":
        await dashboard(update, context)

    elif text == "💱 Calculator":
        await calculator(update, context)

    else:
        await update.message.reply_text("Alege din meniu 👇")


# 🚀 MAIN
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🔥 BOT PORNIT")
    app.run_polling()


if __name__ == "__main__":
    main()
