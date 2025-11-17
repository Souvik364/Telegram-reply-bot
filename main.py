# main.py
import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("8282084436:AAHvjTPt62d764dkmEqad5wH7Ps0WA-_oKs")
ADMIN_ID = int(os.getenv("5154770707", "0"))  # set in environment

# Map: user_id -> asyncio.Event + latest admin reply
pending = {}  # user_id -> {"event": Event, "reply": None}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi — this is the reply bot. Admin will reply soon.")

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text or "<non-text message>"

    # forward message to admin
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"From user {user_id} (@{update.message.from_user.username}):\n\n{text}\n\n"
             f"To reply use: /reply {user_id} <your message>"
    )

    # create an event for this user and wait for admin reply (with timeout)
    evt = asyncio.Event()
    pending[user_id] = {"event": evt, "reply": None}
    # give user a waiting message
    await update.message.reply_text("Contacting admin... (waiting 10s for live reply)")
    try:
        # wait up to 10 seconds for admin reply
        await asyncio.wait_for(evt.wait(), timeout=10.0)
    except asyncio.TimeoutError:
        # no admin reply in time -> send smart auto-reply
        await update.message.reply_text(
            "Admin is currently unavailable — here's an automated reply 🤖:\n\n"
            "Thanks for your message! We'll get back to you as soon as possible."
        )
        # cleanup
        pending.pop(user_id, None)
        return

    # admin replied in time
    reply_text = pending[user_id]["reply"] or "Admin replied but message empty."
    await update.message.reply_text(f"Admin: {reply_text}")
    pending.pop(user_id, None)

async def admin_reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Usage: /reply <user_id> message...
    if update.message.from_user.id != ADMIN_ID:
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /reply <user_id> <message>")
        return
    try:
        user_id = int(args[0])
    except ValueError:
        await update.message.reply_text("First argument must be numeric user_id.")
        return
    text = " ".join(args[1:])
    # if user is waiting, set reply and trigger
    entry = pending.get(user_id)
    if entry:
        entry["reply"] = text
        entry["event"].set()
        await update.message.reply_text(f"Reply sent to {user_id}.")
    else:
        # if user not in pending (not waiting), optionally send direct message
        try:
            await context.bot.send_message(chat_id=user_id, text=f"Admin: {text}")
            await update.message.reply_text(f"User not waiting — direct message sent to {user_id}.")
        except Exception as e:
            await update.message.reply_text(f"Failed to send message: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reply", admin_reply_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_user_message))
    print("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
