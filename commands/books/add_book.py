
from config import bot
from functions.adding_updating import process_title
from variables.globals import media_type


def add_book(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "Як називалася книжка?")
    media_type[chat_id] = 'book'
    bot.register_next_step_handler(msg, process_title)