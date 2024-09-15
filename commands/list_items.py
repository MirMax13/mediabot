from config import bot
import os
from functions.listing import list_items
from variables.globals import query_dict
ADMIN_ID = os.environ.get('ADMIN_ID')

def list_admin_items(message):
    query = {'user_id': int(ADMIN_ID)}
    query_dict[message.chat.id] = query
    list_items(message)

def list_user_items(message):
    chat_id = message.chat.id
    query = {'user_id': chat_id}
    query_dict[chat_id] = query
    list_items(message)

