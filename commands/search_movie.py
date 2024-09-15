from config import bot
from functions.searching import process_search_user, process_search_admin
from variables.globals import media_type

def search_user_movie(message):
    chat_id = message.chat.id
    # msg = bot.send_message(chat_id, "Як називався фільм?")
    media_type[chat_id] = 'film'
    # bot.register_next_step_handler(msg, process_search_user)
    process_search_user(message)

def search_admin_movie(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "Як називався фільм?")
    media_type[chat_id] = 'film'
    bot.register_next_step_handler(msg, process_search_admin)
