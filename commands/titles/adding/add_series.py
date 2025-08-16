from config import bot
from functions.adding_updating import process_title
from variables.globals import media_type, movie_type

def add_series(message):
    chat_id = message.chat.id
    media_type[chat_id] = 'film'
    msg = bot.send_message(chat_id, "Як називається серіал?")
    movie_type[chat_id] = 'series'
    bot.register_next_step_handler(msg, process_title)

