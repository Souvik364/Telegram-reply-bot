import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from google import genai

# --- 1. CONFIGURATION ---
# IMPORTANT: Replace with your actual values
BOT_TOKEN = "8282084436:AAHvjTPt62d764dkmEqad5wH7Ps0WA-_oKs"
ADMIN_USER_ID = 5154770707 # e.g., 123456789
GEMINI_API_KEY = "AIzaSyAu786elfrzrYps7LlX0HRHD8Qd_VbzLTA"

# Bot State - This should ideally be a database in a production environment
admin_available = True 

# Initialize Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)
model = "gemini-2.5-flash" 

# --- 2. SMART REPLY LOGIC (Admin is Unavailable) ---

async def smart_reply(update: Update, context):
    """Generates a smart, helpful reply using Gemini."""
    user_message = update.message.text
    
    # Define the System Prompt for the AI
    system_prompt = (
        "You are an extremely helpful, polite, and professional customer service agent for a small business. "
        "The human Admin is currently unavailable. Respond concisely to the user's message. "
        "Crucially, **always** include a closing statement that apologizes for the Admin's absence and promises a human follow-up as soon as possible."
    )

    try:
        response = client.models.generate_content(
            model=model,
            contents=[
                {"role": "system", "parts": [{"text": system_prompt}]},
                {"role": "user", "parts": [{"text": user_message}]}
            ]
        )
        
        await update.message.reply_text(response.text)
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        await update.message.reply_text(
            "I apologize, but I am currently having technical difficulties. The Admin will contact you as soon as they are available."
        )


# --- 3. BOT HANDLERS ---

async def start_command(update: Update, context):
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text(
        f"Hello! I am your 24/7 reply bot. My Admin is currently {'Available' if admin_available else 'Unavailable'}."
    )

async def handle_message(update: Update, context):
    """Main message handler with Admin check logic."""
    user_id = update.effective_user.id
    
    if user_id == ADMIN_USER_ID:
        # Admin's messages are ignored to avoid infinite loops, but you can add admin commands here.
        return

    if admin_available:
        # Admin is available: Forward message to Admin (or Admin Channel)
        # You would replace this with actual forwarding logic.
        await update.message.reply_text(
            "Thank you! Your message has been forwarded to the Admin. They will reply to you personally shortly."
        )
        # In a real bot, you'd use context.bot.send_message(ADMIN_USER_ID, f"New User Message: {update.message.text}")
    else:
        # Admin is NOT available: Use the Smart Reply function
        await smart_reply(update, context)


# --- 4. ADMIN TOGGLE COMMANDS ---

async def set_available(update: Update, context):
    """Admin-only command to set the bot to available mode."""
    global admin_available
    if update.effective_user.id == ADMIN_USER_ID:
        admin_available = True
        await update.message.reply_text("Admin Mode: **AVAILABLE**. User messages will now be manually handled.")
    else:
        await update.message.reply_text("You are not authorized to use this command.")

async def set_unavailable(update: Update, context):
    """Admin-only command to set the bot to smart reply mode."""
    global admin_available
    if update.effective_user.id == ADMIN_USER_ID:
        admin_available = False
        await update.message.reply_text("Admin Mode: **UNAVAILABLE**. Smart Replies are now active.")
    else:
        await update.message.reply_text("You are not authorized to use this command.")


# --- 5. MAIN BOT INITIALIZATION ---

def main():
    """Start the bot."""
    # Build the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("admin_available", set_available))
    application.add_handler(CommandHandler("admin_unavailable", set_unavailable))
    
    # Handle all other messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    print("Bot is running...")
    application.run_polling(poll_interval=3)

if __name__ == '__main__':
    main()
