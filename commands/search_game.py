from config import bot
from functions.searching import process_search_title
from variables.globals import media_type

def search_game(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "Як називалася гра?")
    media_type[chat_id] = 'game'
    bot.register_next_step_handler(msg, process_search_title)
