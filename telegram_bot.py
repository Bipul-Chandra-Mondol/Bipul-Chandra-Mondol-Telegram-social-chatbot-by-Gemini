import requests
from telegram import Update
from telegram.ext import Updater,Application,CommandHandler,MessageHandler,filters,CallbackContext

# Telegram bot documents: https://docs.python-telegram-bot.org/en/v21.6/telegram.bot.html

# Django Rest api url
# DJANGO_API_URL = "http://127.0.0.1:8000/api/chat/"
DJANGO_API_URL = "https://149f-103-153-230-181.ngrok-free.app/api/chat/"

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! I'm your social chatbot powered by Gemini")
    
async def handle_message(update: Update, context: CallbackContext):
    user = update.message.from_user
    message_text = update.message.text
    
    #data prepare to send Django API
    payload = {
        'telegram_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'message_text': message_text
    }
    
    # print(payload)
    # send user message to django rest api
    response = requests.post(DJANGO_API_URL, json= payload)
    
    # print(response.json().get('reply'))
    if response.status_code == 200:
        bot_reply = response.json().get('reply')
        await update.message.reply_text(bot_reply)
    else:
        await update.message.reply_text("Sorry, something went wrong!")
        
if __name__ == '__main__':
    # configure bot with token
    application = Application.builder().token("Token").build()
    
    # Add command and message handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    #start the Bot
    application.run_polling()