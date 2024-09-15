from functions.list import send_paginated_list

def process_search_title(message, media_type):
    title = message.text
    chat_id = message.chat.id
    send_paginated_list(chat_id, 0, title=title, media_type=media_type)