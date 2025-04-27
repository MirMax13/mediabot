from config import bot
from functions.adding_updating import process_title
from variables.globals import media_type

def add_anime_series(message):
    chat_id = message.chat.id
    media_type[chat_id] = 'anime_series'
    msg = bot.send_message(chat_id, "Як називалось аніме?")
    bot.register_next_step_handler(msg, process_title)

def add_anime_movie(message):
    chat_id = message.chat.id
    media_type[chat_id] = 'anime_movie'
    msg = bot.send_message(chat_id, "Як називалось аніме?")
    bot.register_next_step_handler(msg, process_title)