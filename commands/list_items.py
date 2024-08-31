from telebot import types
from db import db
from bson import ObjectId
from config import bot,params_dict
from commands.add_update_movie import add_movie, ask_for_rating, ask_for_review, ask_for_date, ask_for_conditions
from telebot.util import quick_markup

def list_items(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Обробка команди /list')  # Діагностичне повідомлення
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = ['Фільми', 'Ігри', 'Книги']
    for option in options:
        markup.add(option)
    msg = bot.send_message(chat_id, 'Чого саме список бажаєш?', reply_markup=markup)
    bot.register_next_step_handler(msg, process_list)

def process_list(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Обробка вибору списку')
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = ['Усі що є', 'За роком', 'За кількома роками']
    for option in options:
        markup.add(option)
    msg = bot.send_message(chat_id, 'Який саме список?', reply_markup=markup)
    bot.register_next_step_handler(msg, process_list_type)

def process_list_type(message):
    chat_id = message.chat.id
    list_type = message.text
    bot.send_message(chat_id, f'Обраний тип списку: {list_type}')
    if list_type == 'Усі що є':
        send_paginated_list(chat_id, 0)
    elif list_type == 'За роком':
        msg = bot.send_message(chat_id, 'Введи рік:')
        bot.register_next_step_handler(msg, process_year)
    else:
        msg = bot.send_message(chat_id, 'Введи роки (через пробіл):')
        bot.register_next_step_handler(msg, process_years)


def send_paginated_list(chat_id, page,year=None, years=None, title=None):
    items_per_page = 85
    query = {}
    if title is not None:
        query['title'] = {'$regex': title, '$options': 'i'}
    elif year is not None:
        query['year'] = year
    elif years is not None:
        query['year'] = {'$in': years}

    all_items = list(db.films.find(query).sort('date_watched', 1))
    total_pages = (len(all_items) + items_per_page - 1) // items_per_page
    start = page * items_per_page
    end = start + items_per_page
    items = all_items[start:end]

    markup = types.InlineKeyboardMarkup()
    for item in items:
        title = item.get('title', 'Немає назви')
        rating = item.get('rating', 'Немає оцінки')
        date = item.get('date_watched', 'Немає дати')
        button_text = f"{title} | {rating} | {date}"
        button = types.InlineKeyboardButton(text=button_text, callback_data=f"film_{item['_id']}")
        markup.add(button)

    if page > 0:
        markup.add(types.InlineKeyboardButton(text='Попередня', callback_data=f'page_{page - 1}'))
    if page < total_pages - 1:
        markup.add(types.InlineKeyboardButton(text='Наступна', callback_data=f'page_{page + 1}'))

    bot.send_message(chat_id, f'Сторінка {page + 1} з {total_pages}', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('page_'))
def change_page(call):
    chat_id = call.message.chat.id
    data = call.data.split('_')
    page = int(data[1])
    year = int(data[2]) if len(data) > 2 and data[2] != 'None' else None
    years = list(map(int, data[3].strip('[]').split(','))) if len(data) > 3 and data[3] != 'None' else None
    send_paginated_list(chat_id, page, year=year, years=years)



def process_year(message):
    chat_id = message.chat.id
    year = message.text
    bot.send_message(chat_id, f'Обраний рік: {year}')
    
    try:
        year_int = int(year)
    except ValueError:
        bot.send_message(chat_id, 'Невірний формат року. Введіть, будь ласка, рік у форматі чисел.')
        return
    
    send_paginated_list(chat_id, 0, year=year_int)

def process_years(message):
    chat_id = message.chat.id
    years = message.text.split()
    bot.send_message(chat_id, f'Обрані роки: {years}')

    try:
        years = [int(year) for year in years]
    except ValueError:
        bot.send_message(chat_id, 'Невірний формат року. Введіть, будь ласка, рік у форматі чисел.')
        return

    send_paginated_list(chat_id, 0, years=years)



@bot.callback_query_handler(func=lambda call: call.data.startswith('film_'))
def send_film_info(call):
    chat_id = call.message.chat.id
    film_id = call.data.split('_')[1]
    film = db.films.find_one({'_id': ObjectId(film_id)})
    if film:
        markup = quick_markup({
            'Назад': {'callback_data': 'back_to_list'},
            'Редагувати': {'callback_data': f'edit_film_{film_id}'},
            'Видалити': {'callback_data': f'delete_film_{film_id}'}
        })

        title = film.get('title', 'Немає назви')
        rating = film.get('rating', 'Немає оцінки')
        review = film.get('review', '-')
        year = film.get('year', 'Немає року')
        date_watched = film.get('date_watched', 'Немає дати')
        watch_conditions = film.get('watch_conditions', 'Немає умов перегляду')
        message_text = (f"Назва: {title}\n"
                        f"Оцінка: {rating}\n"
                        f"Відгук: {review}\n"
                        f"Рік: {year}\n"
                        f"Дата перегляду: {date_watched}\n"
                        f"Умови перегляду: {watch_conditions}")
        bot.send_message(chat_id, message_text,reply_markup=markup)
    else:
        bot.send_message(chat_id, 'Фільм не знайдено.')

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_film_'))
def delete_film(call):
    chat_id = call.message.chat.id
    film_id = call.data.split('_')[2]
    db.films.delete_one({'_id': ObjectId(film_id)})
    bot.send_message(chat_id, 'Фільм видалено.')

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_film_'))
def edit_film(call):
    chat_id = call.message.chat.id
    film_id = call.data.split('_')[2]
    params_dict[chat_id] = {'film_id': film_id}
    markup = quick_markup({
        'Редагувати назву': {'callback_data': f'edit_title_{film_id}'},
        'Редагувати оцінку': {'callback_data': f'edit_rating_{film_id}'},
        'Редагувати відгук': {'callback_data': f'edit_review_{film_id}'},
        'Редагувати дату перегляду': {'callback_data': f'edit_date_{film_id}'},
        'Редагувати рік перегляду': {'callback_data': f'edit_year_{film_id}'},
        'Редагувати умови перегляду': {'callback_data': f'edit_conditions_{film_id}'},
        'Редагувати все': {'callback_data': f'edit_all_{film_id}'}
    })
    bot.send_message(chat_id, f'Оберіть, що саме редагувати:{film_id}', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_'))
def edit_smth(call):
    chat_id = call.message.chat.id
    film_id = call.data.split('_')[2]
    attribute = call.data.split('_')[1]
    params_dict[chat_id] = {'film_id': film_id, 'state': f'editing_{attribute}'}
    if attribute == 'title' or attribute == 'all':
        add_movie(call.message)
    elif attribute == 'rating':
        ask_for_rating(call.message)
    elif attribute == 'review':
        ask_for_review(call.message)
    elif attribute == 'date':
        ask_for_date(call.message)
    elif attribute == 'conditions':
        ask_for_conditions(call.message)


@bot.callback_query_handler(func=lambda call: call.data == 'back_to_list')
def back_to_list(call):
    process_list(call.message)