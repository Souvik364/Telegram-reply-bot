from telegram.ext import Updater, MessageHandler, Filters
from telegram import Bot
import threading

TOKEN = 
ADMIN_ID = 

bot = Bot(TOKEN)

pending_replies = {}

def smart_reply(user_id, user_name, user_msg):
    msg = user_msg.lower()

    if "hi" in msg or "hello" in msg:
        return f"Hello {user_name}! The admin will reply soon 😊"
    elif "?" in user_msg:
        return "Thanks for your question! The admin will respond shortly."
    else:
        return "Thank you! The admin will reply as soon as possible."

def send_fallback_reply(user_id, user_name, user_msg):
    if pending_replies.get(user_id, False):
        fallback = smart_reply(user_id, user_name, user_msg)
        bot.send_message(chat_id=user_id, text=fallback)
        pending_replies[user_id] = False

def handle_user_message(update, context):
    user = update.message.from_user
    msg = update.message.text
    uid = user.id

    pending_replies[uid] = True

    bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Message from {user.first_name} (ID: {uid}):\n\n{msg}"
    )

    threading.Timer(15, send_fallback_reply, args=[uid, user.first_name, msg]).start()

def handle_admin_reply(update, context):
    if update.message.reply_to_message:
        reply_text = update.message.text
        text = update.message.reply_to_message.text

        uid = text.split("(ID: ")[1].split("):")[0]
        pending_replies[int(uid)] = False

        bot.send_message(chat_id=uid, text=reply_text)

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(MessageHandler(Filters.chat_type.private & ~Filters.user(ADMIN_ID), handle_user_message))
dp.add_handler(MessageHandler(Filters.user(ADMIN_ID) & Filters.reply, handle_admin_reply))

updater.start_polling()
updater.idle()

