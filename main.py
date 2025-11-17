from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import threading
import os

TOKEN = os.environ.get("8282084436:AAHvjTPt62d764dkmEqad5wH7Ps0WA-_oKs")
ADMIN_ID = int(os.environ.get(5154770707))

pending_replies = {}

def smart_reply(user_name, user_msg):
    msg = user_msg.lower()

    if "hi" in msg or "hello" in msg:
        return f"Hello {user_name}! The admin will reply soon 😊"
    elif "?" in user_msg:
        return "Thanks for your question! The admin will respond shortly."
    else:
        return "Thank you! The admin will reply as soon as possible."

async def send_fallback_reply(app, user_id, user_name, user_msg):
    if pending_replies.get(user_id, False):
        reply = smart_reply(user_name, user_msg)
        await app.bot.send_message(chat_id=user_id, text=reply)
        pending_replies[user_id] = False

async def handle_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    msg = update.message.text
    uid = user.id

    pending_replies[uid] = True

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Message from {user.first_name} (ID: {uid}):\n\n{msg}"
    )

    threading.Timer(15, lambda: 
        context.application.create_task(
            send_fallback_reply(context.application, uid, user.first_name, msg)
        )
    ).start()

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        reply_text = update.message.text
        text = update.message.reply_to_message.text

        uid = text.split("(ID: ")[1].split("):")[0]
        pending_replies[int(uid)] = False

        await context.bot.send_message(chat_id=uid, text=reply_text)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & ~filters.User(ADMIN_ID), handle_user))
app.add_handler(MessageHandler(filters.User(ADMIN_ID) & filters.TEXT, handle_admin_reply))

app.run_polling()
