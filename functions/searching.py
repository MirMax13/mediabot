from functions.listing import send_paginated_list
from variables.globals import query_dict

def process_search_title(message):
    title = message.text
    chat_id = message.chat.id
    query = {'user_id': chat_id} #TODO: change for search_admin
    query_dict[chat_id] = query
    send_paginated_list(chat_id, 0, title=title)