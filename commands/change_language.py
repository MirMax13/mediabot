from config import bot
from variables.globals import user_language
from functions.utils import get_message

def change_language(message):
    chat_id = message.chat.id
    lang = message.text.split()[1]  # Assuming the command is /change_language <lang>
    if lang in ['en', 'uk']:
        user_language[chat_id] = lang
        bot.send_message(chat_id, get_message(chat_id, 'language_changed'))
    else:
        bot.send_message(chat_id, "Unsupported language. Please choose 'en' or 'uk'.")

    