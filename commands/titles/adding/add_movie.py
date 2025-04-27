from config import bot
from functions.adding_updating import process_title
from variables.globals import media_type

def add_movie(message):
    chat_id = message.chat.id
    media_type[chat_id] = 'film'
    msg = bot.send_message(chat_id, "Як називався фільм?")
    bot.register_next_step_handler(msg, process_title)

