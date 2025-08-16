from config import bot
from functions.adding_updating import process_title
from variables.globals import media_type,movie_type,is_waiting
from telebot import types
from commands.titles.adding.add_movie import add_movie
from commands.titles.adding.add_series import add_series
from commands.titles.adding.add_anime import add_anime_series, add_anime_movie
from commands.titles.adding.add_animated import add_animated_movie, add_animated_series

def add_waiting_media(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = ['Фільм', 'Серіал', 'Мультфільм', 'Аніме-фільм', 'Аніме-серіал', 'Мультсеріал']
    for option in options:
        markup.add(types.KeyboardButton(option))
    msg = bot.send_message(chat_id, "Оберіть тип медіа:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_selected_media)

def process_selected_media(message):
    chat_id = message.chat.id
    selected_option = message.text
    is_waiting[chat_id] = True
    if selected_option == 'Серіал':
        add_series(message)
    elif selected_option == 'Мультфільм':
        add_animated_movie(message)
    elif selected_option == 'Мультсеріал':
        add_animated_series(message)
    elif selected_option == 'Аніме-фільм':
        add_anime_movie(message)
    elif selected_option == 'Аніме-серіал':
        add_anime_series(message)
    else:
        add_movie(message)
    
