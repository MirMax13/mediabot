from config import bot
from functions.searching import process_search_title
from variables.globals import media_type

def search_book(message):
    chat_id = message.chat.id
    msg = bot.send_message(message.chat.id, "Як називалася книжка?")
    media_type[chat_id] = 'book'
    bot.register_next_step_handler(msg, process_search_title)
