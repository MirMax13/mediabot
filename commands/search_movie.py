from config import bot
from commands.list_items import send_paginated_list

def search_movie(message):
    msg = bot.send_message(message.chat.id, "Як називався фільм?")
    bot.register_next_step_handler(msg, process_search_title)

def process_search_title(message):
    title = message.text
    chat_id = message.chat.id
    send_paginated_list(chat_id, 0, title=title)