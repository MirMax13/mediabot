
from config import bot
from commands.adding_updating import process_title


def add_book(message):
    msg = bot.send_message(message.chat.id, "Як називалася книжка?")
    bot.register_next_step_handler(msg, process_title, 'book')