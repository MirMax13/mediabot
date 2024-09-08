from telebot import types
from db import db
from bson import ObjectId
from config import bot,params_dict
from commands.adding_updating import ask_for_rating, ask_for_review, ask_for_date, ask_for_conditions,ask_for_author
from commands.add_movie import add_movie
from commands.add_game import add_game
from commands.add_book import add_book
from telebot.util import quick_markup
from telebot.types import Message

def list_items(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = ['Фільми', 'Ігри', 'Книги']
    for option in options:
        markup.add(option)
    msg = bot.send_message(chat_id, 'Чого саме список бажаєш?', reply_markup=markup)
    bot.register_next_step_handler(msg, process_list)

def process_list(message):
    chat_id = message.chat.id
    media_type = message.text
    bot.send_message(chat_id, 'Обробка вибору списку')
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = ['Усі що є', 'За роком', 'За кількома роками']
    for option in options:
        markup.add(option)
    msg = bot.send_message(chat_id, 'Який саме список?', reply_markup=markup)
    bot.register_next_step_handler(msg, process_list_type,media_type)

def process_list_type(message,media_type):
    chat_id = message.chat.id
    list_type = message.text
    bot.send_message(chat_id, f'Обраний тип списку: {list_type}')
    if list_type == 'Усі що є':
        send_paginated_list(chat_id, 0,media_type=media_type)
    elif list_type == 'За роком':
        msg = bot.send_message(chat_id, 'Введи рік:')
        bot.register_next_step_handler(msg, process_year,media_type)
    else:
        msg = bot.send_message(chat_id, 'Введи роки (через пробіл):')
        bot.register_next_step_handler(msg, process_years,media_type)


def send_paginated_list(chat_id, page,year=None, years=None, title=None,media_type=None):
    items_per_page = 85
    query = {}
    if title is not None:
        query['title'] = {'$regex': title, '$options': 'i'}
    elif year is not None:
        query['year'] = year
    elif years is not None:
        query['year'] = {'$in': years}
    if 'фільми' in media_type.lower():
        all_items = list(db.films.find(query).sort('date', 1))
    elif 'книги' in media_type.lower():
        all_items = list(db.books.find(query).sort('date', 1))
    elif 'ігри' in media_type.lower():
        all_items = list(db.games.find(query).sort([('rating', -1), ('title', 1)]))
    total_pages = (len(all_items) + items_per_page - 1) // items_per_page
    start = page * items_per_page
    end = start + items_per_page
    items = all_items[start:end]

    markup = types.InlineKeyboardMarkup()
    for item in items:
        title = item.get('title', 'Немає назви')
        rating = item.get('rating', 'Немає оцінки')
        date = item.get('date', 'Немає дати')
        button_text = f"{title} | {rating} | {date}"
        callback_type = 'game' if 'ігри' in media_type.lower() else 'film' if 'фільми' in media_type.lower() else 'book'
        button = types.InlineKeyboardButton(text=button_text, callback_data=f"{callback_type}_{item['_id']}")
        markup.add(button)

    if page > 0:
        markup.add(types.InlineKeyboardButton(text='Попередня', callback_data=f'page_{page - 1}_{media_type}'))
    if page < total_pages - 1:
        markup.add(types.InlineKeyboardButton(text='Наступна', callback_data=f'page_{page + 1}_{media_type}'))

    bot.send_message(chat_id, f'Сторінка {page + 1} з {total_pages}', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('page_'))
def change_page(call):
    chat_id = call.message.chat.id
    data = call.data.split('_')
    page = int(data[1])
    media_type = data[2]
    year = int(data[4]) if len(data) > 4 and data[4] != 'None' else None
    years = list(map(int, data[4].strip('[]').split(','))) if len(data) > 4 and data[4] != 'None' else None
    send_paginated_list(chat_id, page, year=year, years=years,media_type=media_type)

def process_year(message,media_type):
    chat_id = message.chat.id
    year = message.text
    bot.send_message(chat_id, f'Обраний рік: {year}')
    
    try:
        year_int = int(year)
    except ValueError:
        bot.send_message(chat_id, 'Невірний формат року. Введіть, будь ласка, рік у форматі чисел.')
        return
    
    send_paginated_list(chat_id, 0, year=year_int, media_type=media_type)

def process_years(message,media_type):
    chat_id = message.chat.id
    years = message.text.split()
    bot.send_message(chat_id, f'Обрані роки: {years}')

    try:
        years = [int(year) for year in years]
    except ValueError:
        bot.send_message(chat_id, 'Невірний формат року. Введіть, будь ласка, рік у форматі чисел.')
        return

    send_paginated_list(chat_id, 0, years=years, media_type=media_type)

@bot.callback_query_handler(func=lambda call: call.data.startswith(('film_', 'game_', 'book_')))
def send_media_info(call):
    chat_id = call.message.chat.id
    media_type, media_id = call.data.split('_')
    media = db[media_type + 's'].find_one({'_id': ObjectId(media_id)})
    if media:
        markup = quick_markup({
            'Назад': {'callback_data': f'back_to_list_{media_type}'},
            'Редагувати': {'callback_data': f'edit_{media_type}_{media_id}'},
            'Видалити': {'callback_data': f'delete_{media_type}_{media_id}'}
        })

        title = media.get('title', 'Немає назви')
        rating = media.get('rating', 'Немає оцінки')
        review = media.get('review', '-')
        year = media.get('year', 'Немає року')
        date = media.get('date', 'Немає дати')
        
        if media_type == 'film' or media_type == 'game':
            conditions = media.get('conditions', 'Немає умов')
            
        if media_type == 'film':
            message_text = (f"Назва: {title}\n"
                            f"Оцінка: {rating}\n"
                            f"Відгук: {review}\n"
                            f"Рік: {year}\n"
                            f"Дата перегляду: {date}\n"
                            f"Умови перегляду: {conditions}")
        elif media_type == 'game':
            message_text = (f"Назва: {title}\n"
                            f"Оцінка: {rating}\n"
                            f"Відгук: {review}\n"
                            f"Рік: {year}\n"
                            f"Дата: {date}\n"
                            f"Умови: {conditions}")
        elif media_type == 'book':
            author = media.get('author', 'Немає автора')
            message_text = (f"Назва: {title}\n"
                            f"Автор: {author}\n"
                            f"Оцінка: {rating}\n"
                            f"Відгук: {review}\n"
                            f"Рік: {year}\n"
                            f"Дата: {date}\n")
        bot.send_message(chat_id, message_text,reply_markup=markup)
    else:
        bot.send_message(chat_id, 'Нічого не знайдено.')

@bot.callback_query_handler(func=lambda call: call.data.startswith(('delete_film_', 'delete_game_', 'delete_book_')))
def delete_media(call):
    chat_id = call.message.chat.id
    media_type, media_id = call.data.split('_')[1:]
    db[media_type + 's'].delete_one({'_id': ObjectId(media_id)})
    if media_type == 'film':
        msg = 'Фільм видалено.'
    elif media_type == 'game':
        msg = 'Гру видалено.'
    elif media_type == 'book':
        msg = 'Книгу видалено.'
    bot.send_message(chat_id, msg)

@bot.callback_query_handler(func=lambda call: call.data.startswith(('edit_film_', 'edit_game_', 'edit_book_')))
def edit_media(call):
    chat_id = call.message.chat.id
    media_type, media_id = call.data.split('_')[1:]
    params_dict[chat_id] = {'media_id': media_id}
    options = {
        'Редагувати назву': {'callback_data': f'edit_title_{media_type}_{media_id}'},
        'Редагувати оцінку': {'callback_data': f'edit_rating_{media_type}_{media_id}'},
        'Редагувати відгук': {'callback_data': f'edit_review_{media_type}_{media_id}'},
        'Редагувати дату': {'callback_data': f'edit_date_{media_type}_{media_id}'},
        'Редагувати все': {'callback_data': f'edit_all_{media_type}_{media_id}'}
    }
    if media_type in ['film', 'game']:
        options['Редагувати умови'] = {'callback_data': f'edit_conditions_{media_type}_{media_id}'}
    elif media_type == 'book':
        options['Редагувати автора'] = {'callback_data': f'edit_author_{media_type}_{media_id}'}
    
    markup = quick_markup(options)
    bot.send_message(chat_id, f'Оберіть, що саме редагувати:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_'))
def edit_smth(call):
    chat_id = call.message.chat.id
    attribute, media_type, media_id = call.data.split('_')[1:]
    params_dict[chat_id] = {'media_id': media_id, 'media_type': media_type,'state': f'editing_{attribute}'}
    if attribute == 'title' or attribute == 'all':
        if media_type == 'film': 
            add_movie(call.message)
        elif media_type == 'game':
            add_game(call.message)
        elif media_type == 'book':
            add_book(call.message)
    elif attribute == 'rating':
        ask_for_rating(call.message,media_type)
    elif attribute == 'review':
        ask_for_review(call.message,media_type)
    elif attribute == 'date':
        ask_for_date(call.message,media_type)
    elif attribute == 'conditions':
        ask_for_conditions(call.message,media_type)
    elif attribute == 'author':
        ask_for_author(call.message,media_type)
        
@bot.callback_query_handler(func=lambda call: call.data.startswith('back_to_list_'))
def back_to_list(call):
    media_type = call.data.split('_')[3]
    if media_type == 'film':
        media_type = 'Фільми'
    elif media_type == 'game':
        media_type = 'Ігри'
    elif media_type == 'book':
        media_type = 'Книги'

    message = Message(
        message_id=call.message.message_id,
        from_user=call.from_user,
        date=call.message.date,
        chat=call.message.chat,
        content_type='text',
        options={},
        json_string=None,
    )
    message.text = media_type  # Встановлення тексту повідомлення

    process_list(message)