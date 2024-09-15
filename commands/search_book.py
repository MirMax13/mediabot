from config import bot
from functions.searching import process_search_user, process_search_admin
from variables.globals import media_type

def search_user_book(message):
    chat_id = message.chat.id
    msg = bot.send_message(message.chat.id, "Як називалася книжка?")
    media_type[chat_id] = 'book'
    bot.register_next_step_handler(msg, process_search_user)

def search_admin_book(message):
    chat_id = message.chat.id
    msg = bot.send_message(message.chat.id, "Як називалася книжка?")
    media_type[chat_id] = 'book'
    bot.register_next_step_handler(msg, process_search_admin)