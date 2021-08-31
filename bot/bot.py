import os
import json
import logging
import pymongo
import datetime
import telegram
from telegram import Update
from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
from telegram.ext import MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import scraper


# Setup logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s -%(message)s',
        level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config file
config = json.load(open("config.json"))

# Create the database client
client = pymongo.MongoClient(config["db"]["host"], config["db"]["port"])
db = client[config["db"]["db_name"]]

API_KEY = "your-telegram-bot-api-key"


def start(update, context) -> None:
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id, text=config["messages"]["start"].format(update["message"]["chat"]["first_name"], parse_mode="Markdown", disable_web_page_preview="True")
    )


def search(update, context) -> None:
    chat_id = update.effective_chat.id
    text = update.message.text

    if text == '/search':
        context.bot.send_message(
            chat_id=chat_id, text=config["messages"]["search_help"]
        )
    else:
        text = " ".join(text.split(' ')[1:])
        query = text.split(':')
        paper = query[0].strip()
        limit = query[-1].strip()

        if not limit.isdigit():
            limit = 5
        limit = int(limit)

        # Save query
        if not db.users.find_one({"chat_id": chat_id}):
            db.users.insert_one(
                    {"chat_id": chat_id, "last_query": None, "limit": None, "offset": None})
        db.users.update_one({"chat_id": chat_id}, {"$set": {"last_query": paper, "limit": limit, "offset": limit}})

        data = scraper.semantic_scholar_query(paper, limit=limit, timeout=15)

        if data:
            parsed_data = scraper.parse_titles(data)
            links = scraper.extract_paper_links(parsed_data)

            for paper, link in links.items():
                # skip papers without valid link(s)
                if not bool(link):
                    continue
                context.bot.send_message(
                        chat_id=chat_id, text=config["messages"]["paper"].format(paper, "\n".join("Link #{} - {}".format(c, i) for c, i in enumerate(link, start=1)))
                )

            keyboard = [[InlineKeyboardButton("More", callback_data="More")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            #update.message.reply_text("Select More", reply_markup=reply_markup)
            context.bot.send_message(chat_id=chat_id, text="Click to view more", reply_markup=reply_markup)
        else:
            context.bot.send_message(chat_id=chat_id, text="Error parsing search query, please retry!")


def button(update, context) -> None:
    chat_id = update.effective_chat.id
    query = update.callback_query

    # Answer CallbackQuery
    query.answer()

    # Extract users last query to parse 'More' into request
    user = db.users.find_one({"chat_id": chat_id})
    if not user:
        return

    data = scraper.semantic_scholar_query(user["last_query"], limit=user["limit"], offset=user["offset"]+1)
    if data:
        parsed_data = scraper.parse_titles(data)
        links = scraper.extract_paper_links(parsed_data)

        for paper, link in links.items():
            # skip papers without valid link(s)
            if not bool(link):
                continue
            context.bot.send_message(
                    chat_id=chat_id, text=config["messages"]["paper"].format(paper, "\n".join("Link #{} - {}".format(c, i) for c, i in enumerate(link, start=1)))               )

    db.users.update_one({"chat_id": chat_id}, {"$set": {"offset": user["offset"]+user["limit"]}})

    keyboard = [[InlineKeyboardButton("More", callback_data="More")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=chat_id, text="Click to view more", reply_markup=reply_markup)


# Parse unknown commands
def unknown(update, context) -> None:
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id, text="Sorry, I don't understand that command."
    )


def main() -> None:
    # Create the Updater and pass the bot's token
    updater = Updater(token=API_KEY, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler("start", start)
    search_handler = CommandHandler("search", search)

    # Register unknown handler last
    unknown_handler = MessageHandler(Filters.command, unknown)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(search_handler)
    dispatcher.add_handler(CallbackQueryHandler(button))

    # Add 'unknown' handler to dispatcher last
    dispatcher.add_handler(unknown_handler)

    # Start the bot
    updater.start_polling()

    # Run the bot until `Ctrl-c` or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
