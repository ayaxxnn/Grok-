# main.py
from flask import Flask
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import database
import config
import asyncio
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize bot
bot = Bot(token=config.BOT_TOKEN)
application = Application.builder().token(config.BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if database.is_banned(update.effective_user.id):
        await update.message.reply_text("You are banned from using this bot.")
        return
    await update.message.reply_text(
        "Welcome To Aizen Bot ⚡️\n"
        "Please Use this /redeem Command For Get Prime video 🧑‍💻\n"
        "For Premium use This Command /premium"
    )

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if database.is_banned(user_id):
        await update.message.reply_text("You are banned from using this bot.")
        return
    if database.is_user_premium(user_id):
        # Premium users have unlimited redeems
        await update.message.reply_text("Processing your redeem request...")
        await bot.send_message(
            chat_id=config.ADMIN_ID,
            text=f"Premium User {user_id} used /redeem"
        )
    elif database.is_unlimited_redeem():
        # Unlimited redeem mode is ON
        await update.message.reply_text("Processing your redeem request...")
        await bot.send_message(
            chat_id=config.ADMIN_ID,
            text=f"Free User {user_id} used /redeem (Unlimited Mode)"
        )
    elif database.has_used_redeem(user_id):
        # Free user already used redeem
        await update.message.reply_text("Please Purchase Premium Key For Use 🗝️")
    else:
        # First-time redeem for free user
        database.set_redeem_used(user_id)
        await update.message.reply_text("Processing your redeem request...")
        await bot.send_message(
            chat_id=config.ADMIN_ID,
            text=f"Free User {user_id} used /redeem"
        )

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if database.is_banned(user_id):
        await update.message.reply_text("You are banned from using this bot.")
        return
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /premium <key>")
        return
    key = context.args[0]
    days = database.validate_key(key)
    if days:
        database.activate_premium(user_id, days)
        await update.message.reply_text("Premium Activated ⚡️")
        await bot.send_message(
            chat_id=config.ADMIN_ID,
            text=f"User {user_id} activated premium with key {key} for {days} days"
        )
    else:
        await update.message.reply_text("Invalid or used key.")

async def genk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != config.ADMIN_ID:
        await update.message.reply_text("You are not authorized.")
        return
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /genk <days>")
        return
    days = int(context.args[0])
    key = database.generate_key(days)
    await update.message.reply_text(f"Generated Key: {key} (Valid for {days} days)")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != config.ADMIN_ID:
        await update.message.reply_text("You are not authorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    message = " ".join(context.args)
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = c.fetchall()
    conn.close()
    for user_id in users:
        try:
            await bot.send_message(chat_id=user_id[0], text=message)
        except:
            pass
    await update.message.reply_text("Broadcast sent.")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != config.ADMIN_ID:
        await update.message.reply_text("You are not authorized.")
        return
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /ban <user_id>")
        return
    user_id = int(context.args[0])
    database.ban_user(user_id)
    await update.message.reply_text(f"User {user_id} banned.")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != config.ADMIN_ID:
        await update.message.reply_text("You are not authorized.")
        return
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /unban <user_id>")
        return
    user_id = int(context.args[0])
    database.unban_user(user_id)
    await update.message.reply_text(f"User {user_id} unbanned.")

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != config.ADMIN_ID:
        await update.message.reply_text("You are not authorized.")
        return
    if len(context.args) < 2 or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /reply <user_id> <message>")
        return
    user_id = int(context.args[0])
    message = " ".join(context.args[1:])
    try:
        await bot.send_message(chat_id=user_id, text=message)
        await update.message.reply_text(f"Message sent to {user_id}")
    except:
        await update.message.reply_text(f"Could not send message to {user_id}")

async def on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != config.ADMIN_ID:
        await update.message.reply_text("You are not authorized.")
        return
    database.set_unlimited_redeem(1)
    await update.message.reply_text("Unlimited redeem mode ON.")

async def off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != config.ADMIN_ID:
        await update.message.reply_text("You are not authorized.")
        return
    database.set_unlimited_redeem(0)
    await update.message.reply_text("Unlimited redeem mode OFF.")

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("redeem", redeem))
application.add_handler(CommandHandler("premium", premium))
application.add_handler(CommandHandler("genk", genk))
application.add_handler(CommandHandler("broadcast", broadcast))
application.add_handler(CommandHandler("ban", ban))
application.add_handler(CommandHandler("unban", unban))
application.add_handler(CommandHandler("reply", reply))
application.add_handler(CommandHandler("on", on))
application.add_handler(CommandHandler("off", off))

# Flask route to keep Render happy
@app.route('/')
def home():
    return "Aizen Bot is running!"

# Run polling in a separate thread
def run_polling():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    database.init_db()  # Initialize database
    application.run_polling()

if __name__ == '__main__':
    import threading
    polling_thread = threading.Thread(target=run_polling)
    polling_thread.start()
    app.run(host='0.0.0.0', port=5000)