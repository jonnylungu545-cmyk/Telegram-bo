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


# 🌍 TEXTE MULTILIMBĂ
TEXTS = {
    "ro": {
        "menu": "✔ Română",
        "choose_crypto": "💳 Alege criptomoneda:",
        "history_empty": "📭 Fără plăți",
        "send_address": "📩 Trimite:\n\n- adresă {crypto}\n- suma (ex: 0.5)",
        "wrong_format": "❌ Format greșit\nEx: ADRESA 0.5",
        "you_get": "💰 Vei primi:\n{amount} {crypto}\n\n💵 De plătit: {lei:.2f} MDL\n\n📱 MIA: {mia}\n🏦 Bpay: {bpay}\n\n👇 După plată apasă:",
        "paid_btn": "✅ Am plătit"
    },
    "ru": {
        "menu": "✔ Русский",
        "choose_crypto": "💳 Выберите криптовалюту:",
        "history_empty": "📭 Нет платежей",
        "send_address": "📩 Отправь:\n\n- адрес {crypto}\n- сумму (например: 0.5)",
        "wrong_format": "❌ Неверный формат\nПример: АДРЕС 0.5",
        "you_get": "💰 Ты получишь:\n{amount} {crypto}\n\n💵 К оплате: {lei:.2f} MDL\n\n📱 MIA: {mia}\n🏦 Bpay: {bpay}\n\n👇 После оплаты нажми:",
        "paid_btn": "✅ Я оплатил"
    }
}


def t(user_id, key):
    lang = user_lang.get(user_id, "ro")
    return TEXTS[lang][key]


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

menu_ru = ReplyKeyboardMarkup(
    [["💳 Обмен крипто", "📜 История"]],
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
        await q.message.reply_text(t(user_id, "send_address").format(crypto="BTC"))

    elif q.data == "ltc":
        user_step[user_id] = "WAIT_ADDRESS"
        user_data_temp[user_id] = {"crypto": "LTC"}
        await q.message.reply_text(t(user_id, "send_address").format(crypto="LTC"))

    elif q.data == "confirm_pay":
        data = user_data_temp.get(user_id)
        user = q.from_user
        username = f"@{user.username}" if user.username else "NU ARE USERNAME"

        await q.message.reply_text("⏳ Plata în verificare (5-10 min)")

        keyboard = [
            [InlineKeyboardButton("✅ Trimite TXID", callback_data=f"sendtx_{user_id}")]
        ]

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"💰 COMANDĂ NOUĂ\n\n"
                f"👤 User: {username}\n"
                f"🆔 ID: {user_id}\n\n"
                f"{data['amount']} {data['crypto']}\n"
                f"≈ {data['lei']:.2f} MDL\n\n"
                f"📩 Adresă:\n{data['address']}"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif q.data.startswith("sendtx_"):
        target_user = int(q.data.split("_")[1])
        user_step[ADMIN_ID] = f"SEND_TX_{target_user}"
        await q.message.reply_text("✏️ Trimite TXID sau link blockchain:")


# 💳 START PLATĂ
async def payments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    keyboard = [
        [
            InlineKeyboardButton("₿ BTC", callback_data="btc"),
            InlineKeyboardButton("Ł LTC", callback_data="ltc")
        ]
    ]

    await update.message.reply_text(
        t(user_id, "choose_crypto"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# 📜 ISTORIC
async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    db = load_db()
    uid = str(user_id)

    data = db.get(uid, [])

    if not data:
        await update.message.reply_text(t(user_id, "history_empty"))
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
        await update.message.reply_text(TEXTS["ro"]["menu"], reply_markup=menu_ro)
        return

    if text == "🇷🇺 Русский":
        user_lang[user_id] = "ru"
        await update.message.reply_text(TEXTS["ru"]["menu"], reply_markup=menu_ru)
        return

    # meniu RO
    if text == "💳 Schimb Crypto" or text == "💳 Обмен крипто":
        await payments(update, context)
        return

    if text == "📜 Istoric" or text == "📜 История":
        await history(update, context)
        return

    # ADMIN TRIMITE TXID
    if user_id == ADMIN_ID and user_step.get(user_id, "").startswith("SEND_TX_"):
        target_user = int(user_step[user_id].split("_")[2])

        tx_link = text

        await context.bot.send_message(
            chat_id=target_user,
            text=f"✅ Transfer trimis!\n\n🔗 Link:\n{tx_link}"
        )

        await update.message.reply_text("✅ Trimis către client")

        user_step.pop(user_id)
        return

    # PAS 1
    if user_step.get(user_id) == "WAIT_ADDRESS":
        try:
            parts = text.split()
            address = parts[0]
            amount = float(parts[1])
        except:
            await update.message.reply_text(t(user_id, "wrong_format"))
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
            [InlineKeyboardButton(t(user_id, "paid_btn"), callback_data="confirm_pay")]
        ]

        await update.message.reply_text(
            t(user_id, "you_get").format(
                amount=amount,
                crypto=crypto,
                lei=lei,
                mia=MIA_PHONE,
                bpay=BPAY_ACCOUNT
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        user_step.pop(user_id)

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
