import os
import json
import logging
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import scraper


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s -%(message)s',
        level=logging.INFO)
logger = logging.getLogger(__name__)

config = json.load(open("config.json"))
#API_KEY = "your-telegram-bot-api-key"

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
        data = scraper.semantic_scholar_query(text)

        if data:
            parsed_data = scraper.parse_titles(data)
            links = scraper.extract_paper_links(parsed_data)

            for paper, link in links.items():
                context.bot.send_message(
                        chat_id=chat_id, text=config["messages"]["paper"].format(paper, "\n".join("Link #{} - {}".format(c, i) for c, i in enumerate(link, start=1)))
                )
        else:
            context.bot.send_message(chat_id=chat_id, text="Error parsing search query, please retry!")

def unknown(update, context) -> None:
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id, text="Sorry, I don't understand that command."
    )

def main() -> None:
    #Create the Updater and pass the bot's token
    updater = Updater(token=API_KEY, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler("start", start)
    search_handler = CommandHandler("search", search)
    unknown_handler = MessageHandler(Filters.command, unknown)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(search_handler)
    dispatcher.add_handler(unknown_handler)

    # Start the bot
    updater.start_polling()

    # Run the bot until `Ctrl-c` or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
