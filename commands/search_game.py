from functions.searching import process_search_user, process_search_admin
from variables.globals import media_type

def search_user_game(message):
    # TODO: Refactor
    chat_id = message.chat.id
    media_type[chat_id] = 'game'
    process_search_user(message)

def search_admin_game(message):
    chat_id = message.chat.id
    media_type[chat_id] = 'game'
    process_search_admin(message)
