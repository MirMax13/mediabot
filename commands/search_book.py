from config import bot
from functions.searching import process_search_title

def search_book(message):
    msg = bot.send_message(message.chat.id, "Як називалася книжка?")
    bot.register_next_step_handler(msg, process_search_title, media_type='книги')
