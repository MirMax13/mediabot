from functions.listing import send_paginated_list
from variables.globals import query_dict, media_type
import os
from config import bot
from telebot import types

ADMIN_ID = os.getenv('ADMIN_ID')

messages = {
    'film': {
        'name': "Як називався фільм?",

    },
    'game': {
        'name': "Як називалася гра?",
    },
    'book': {
        'name': "Як називалася книга?",
    }
}

def process_search_user(message):
    chat_id = message.chat.id
    query = {'user_id': chat_id}
    query_dict[chat_id] = query
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = ['По назві', 'По жанру', 'По рейтингу', 'По відгуку', 'По році','По умовах']
    for option in options:
        markup.add(option)
    msg = bot.send_message(chat_id, "По чому шукати?", reply_markup=markup)
    bot.register_next_step_handler(msg, process_search_option)

def process_search_admin(message): 
    # TODO: Refactor
    chat_id = message.chat.id
    query = {'user_id': int(ADMIN_ID)}
    query_dict[chat_id] = query
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = ['По назві', 'По жанру', 'По рейтингу', 'По відгуку', 'По році','По умовах']
    for option in options:
        markup.add(option)
    msg = bot.send_message(chat_id, "По чому шукати?", reply_markup=markup)
    bot.register_next_step_handler(msg, process_search_option)

def process_search_option(message):
    chat_id = message.chat.id
    option = message.text
    if option == 'По назві':
        search_query = 'title'
        msg = bot.send_message(chat_id, messages[media_type[chat_id]]['name'])
    
    # elif option == 'По жанру': #TODO: Add 'По жанру'
    #     if media_type[chat_id] == 'book':
    #         search_query = 'genre'
    #         msg = bot.send_message(chat_id, "Який жанр?")
    #     else:
    #         msg = bot.send_message(chat_id, "Жанри доступні тільки для книг. Оберіть інший варіант.")
    #         bot.register_next_step_handler(msg, process_search_option)
    elif option == 'По рейтингу':
        search_query = 'rating'
        msg = bot.send_message(chat_id, "Який рейтинг?")
    elif option == 'По відгуку':
        search_query = 'review'
        msg = bot.send_message(chat_id, "Введіть текст відгуку")
    elif option == 'По році':
        search_query = 'year'
        msg = bot.send_message(chat_id, "Котрого року шукати?")
    elif option == 'По умовах':
        if media_type[chat_id] == 'film' or media_type[chat_id] == 'game':
            search_query = 'conditions'
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            if media_type[chat_id] == 'film':
                options = ['Сам вдома', 'З кимось вдома', 'На великих екранах', 'Невідомо', 'Інше']
            elif media_type[chat_id] == 'game':
                ['Пройшов', 'Подивився', 'Грав', 'Дивився',
                    'Подивився повністю, а потім зіграв',
                    'Подивився повністю, а потім пройшов повністю',
                    'Дивився, а потім зіграв','Слухав сюжет',
                    'Дивився, а потім слухав сюжет, а потім зіграв','Дивився, а потім слухав сюжет',
                    'Грав (неможливо пройти)','Дивився, а потім грав (неможливо пройти)',
                    'Пройшов разом з DLC','Дивився, а потім пройшов разом з DLC',
                    'Невідомо']
            for option in options:
                markup.add(option)
            if media_type[chat_id] == 'film':
                msg = bot.send_message(chat_id, 'Як ти дивився?', reply_markup=markup)
            elif media_type[chat_id] == 'game':
                msg = bot.send_message(chat_id, 'Грав/дивився?', reply_markup=markup)
        else:
            msg = bot.send_message(chat_id, "Умови доступні тільки для фільмів та ігор. Оберіть інший варіант.")
            bot.register_next_step_handler(msg, process_search_option)
    else:
        msg = bot.send_message(chat_id, "Оберіть один з варіантів (окрім жанру).")
        bot.register_next_step_handler(msg, process_search_option)
    bot.register_next_step_handler(msg, process_search, option=search_query)
    
def process_search(message,option):
    chat_id = message.chat.id
    search_query = message.text
    if option == 'rating':
        try:
            search_query = float(search_query)
        except ValueError:
            bot.send_message(chat_id, "Будь ласка, введіть дійсний рейтинг.")
            return
    send_paginated_list(chat_id, 0, option=option, search_query=search_query)