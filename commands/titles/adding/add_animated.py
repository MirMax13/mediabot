from config import bot
from functions.adding_updating import process_title
from variables.globals import media_type, movie_type

def add_animated_series(message):
    chat_id = message.chat.id
    media_type[chat_id] = 'film'
    msg = bot.send_message(chat_id, "Як називається мультсеріал?")
    movie_type[chat_id] = 'animated_series'
    bot.register_next_step_handler(msg, process_title)

def add_animated_movie(message):
    chat_id = message.chat.id
    media_type[chat_id] = 'film'
    msg = bot.send_message(chat_id, "Як називається мульфільм?")
    movie_type[chat_id] = 'animated_movie'
    bot.register_next_step_handler(msg, process_title)