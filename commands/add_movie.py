from config import bot
from commands.adding_updating import process_title

def add_movie(message):
    msg = bot.send_message(message.chat.id, "Як називався фільм?")
    bot.register_next_step_handler(msg, process_title, 'film')

