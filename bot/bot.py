import os
import logging
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s -%(message)s',
        level=logging.INFO)

API_KEY = ""

updater = Updater(token=API_KEY, use_context=True)
dispatcher = updater.dispatcher

def start(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id, text="hi"
    )

def search(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id, text="search"
    )

def unknown(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id, text="Sorry, I don't understand that command."
    )

start_handler = CommandHandler("start", start)
search_handler = CommandHandler("search", search)
unknown_handler = MessageHandler(Filters.command, unknown)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(search_handler)
dispatcher.add_handler(unknown_handler)

updater.start_polling()
