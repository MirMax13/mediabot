from variables.globals import user_language
from variables.languages import languages

def get_message(chat_id, message_key):
    lang = user_language.get(chat_id, 'uk')  # Default to Ukrainian
    return languages[lang].get(message_key, '')