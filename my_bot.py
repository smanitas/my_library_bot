import bot_logging
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)
import requests
import logging
import os

# Set up basic logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    logger.info(f"User: {user_id} executed command: /start")
    update.message.reply_text(
        "Hello! Just send me a book title or an author's name, and I'll try to find it for you."
    )


def search_book_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    query = " ".join(context.args) if context.args else update.message.text
    logger.info(f"Received search query: '{query}' from user: {user_id}")
    try:
        response = requests.get(
            f"https://openlibrary.org/search.json?q={query}&fields=key,title,author_name,cover_i,first_publish_year"
        )

        if response.status_code == 200:
            data = response.json()
            num_results = data["num_found"]
            logger.info(f"Query '{query}' processed. Number of results: {num_results}.")
            if num_results > 0:
                message = "Here's what I found:\n\n"
                for doc in data["docs"][:5]:
                    title = doc.get("title", "No title available")
                    author_name = ", ".join(doc.get("author_name", ["No author"]))
                    first_publish_year = doc.get("first_publish_year", "N/A")
                    cover_id = doc.get("cover_i")
                    book_key = doc.get("key", "")
                    cover_url = (
                        f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
                        if cover_id
                        else "No cover available"
                    )
                    book_url = f"https://openlibrary.org{book_key}"
                    message += f"Title: {title}\nAuthor: {author_name}\nYear: {first_publish_year}\nCover: {cover_url}\nMore Info: {book_url}\n\n"
                update.message.reply_text(
                    message
                    if num_results > 0
                    else "I couldn't find any books matching your query."
                )
            else:
                update.message.reply_text(
                    "I couldn't find any books matching your query."
                )
        else:
            logger.error(
                f"Error fetching data from Open Library for query '{query}'. HTTP Status: {response.status_code}"
            )
            update.message.reply_text("There was a problem fetching the book data.")
    except Exception as e:
        logger.error(
            f"Exception occurred while processing query '{query}': {e}", exc_info=True
        )
        update.message.reply_text("An error occurred while fetching book data.")


def error(update: Update, context: CallbackContext) -> None:
    logger.warning("Update '%s' caused error '%s'", update, context.error)


def main() -> None:
    updater = Updater(os.getenv("TELEGRAM_TOKEN"), use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, search_book_message))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
