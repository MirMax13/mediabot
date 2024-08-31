
from config import bot

def add_book(message):
    bot.reply_to(message, "What is the title of the book?")
    bot.register_next_step_handler(message, add_book_title)

def add_book_title(message):
    book_title = message.text
    bot.reply_to(message, f"Book title is {book_title}")