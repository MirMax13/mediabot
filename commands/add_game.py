from config import bot
from commands.adding_updating import process_title

def add_game(message):
    msg = bot.send_message(message.chat.id, "Яка назва гри?")
    bot.register_next_step_handler(msg, process_title, 'game')
    