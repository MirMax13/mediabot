from telebot import types
from db import db
from bson import ObjectId
from config import bot,params_dict
from functions.adding_updating import ask_for_rating, ask_for_review, ask_for_date, ask_for_conditions,ask_for_author,ask_for_type
from functions.markup_buttons import markup_buttons
from commands.titles.adding.add_movie import add_movie
from commands.games.add_game import add_game
from commands.books.add_book import add_book
from telebot.util import quick_markup
from telebot.types import Message
from variables.globals import query_dict, media_type, sort_preference,movie_type

def list_items(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    options = ['Ігри', 'Книги', 'Медіа']
    for option in options:
        button = types.InlineKeyboardButton(option, callback_data=f"main_{option.lower()}")
        markup.add(button)
    current_sort = sort_preference.get(chat_id, "date")
    sort_preference[chat_id] = current_sort
    rating_button = types.InlineKeyboardButton(
        f"{'✓ ' if current_sort == 'rating' else ''} За рейтингом", callback_data="sort_rating"
    )
    date_button = types.InlineKeyboardButton(
        f"{'✓ ' if current_sort == 'date' else ''} За датою", callback_data="sort_date"
    )
    markup.add(rating_button, date_button)
    bot.send_message(chat_id, 'Що саме цікавить?', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("main_"))
def handle_main_selection(call):
    chat_id = call.message.chat.id
    selected_main = call.data.split("_")[1]
    
    if selected_main == 'медіа':
        markup = types.InlineKeyboardMarkup(row_width=1)
        options = ['Фільми', 'Серіали', 'Аніме', 'Мультфільми','Усе']
        for option in options:
            button = types.InlineKeyboardButton(option, callback_data=f"media_{option.lower()}")
            markup.add(button)
        bot.send_message(chat_id, 'Окей, яке саме медіа?', reply_markup=markup)
    else:
        media_type[chat_id] = selected_main
        process_list(selected_main, chat_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("media_"))
def handle_media_selection(call):
    chat_id = call.message.chat.id
    selected_media = call.data.split("_")[1]
    
    if selected_media in ['аніме', 'мультфільми']:
        markup = types.InlineKeyboardMarkup(row_width=1)
        if selected_media == 'аніме':
            options = ['Аніме фільми', 'Аніме серіали', 'Усе аніме']
        else:
            options = ['Мультфільми', 'Мультсеріали', 'Усе мультики']
        for option in options:
            button = types.InlineKeyboardButton(option, callback_data=f"submedia_{option.lower().replace(' ', '_')}")
            markup.add(button)
        bot.send_message(chat_id, 'Що саме?', reply_markup=markup)
    else:
        media_type[chat_id] = 'film'
        if selected_media == 'фільми':
            movie_type[chat_id] = 'film'
        elif selected_media == 'серіали':
            movie_type[chat_id] = 'series'
        else:
            movie_type[chat_id] = 'media'
        process_list(selected_media, chat_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("submedia_"))
def handle_submedia_selection(call):
    chat_id = call.message.chat.id
    selected_submedia = call.data.split("_", 1)[1]
    
    media_type[chat_id] = 'film'
    if selected_submedia == 'аніме_фільми':
        movie_type[chat_id] = 'anime_movies'
    elif selected_submedia == 'аніме_серіали':
        movie_type[chat_id] = 'anime_series'
    elif selected_submedia == 'усе_аніме':
        movie_type[chat_id] = 'anime'
    elif selected_submedia == 'мультфільми':
        movie_type[chat_id] = 'animated_movie'
    elif selected_submedia == 'мультсеріали':
        movie_type[chat_id] = 'animated_series'
    elif selected_submedia == 'усе_мультики':
        movie_type[chat_id] = 'animated'
    elif selected_submedia == 'усе':
        movie_type[chat_id] = 'media'
    
    process_list(selected_submedia, chat_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("type_"))
def handle_type_selection(call):
    chat_id = call.message.chat.id
    selected_type = call.data.split("_")[1]
    media_type[chat_id] = selected_type
    process_list(selected_type,chat_id)

@bot.callback_query_handler(func=lambda call: call.data in ["sort_rating", "sort_date"])
def handle_sort_selection(call):
    chat_id = call.message.chat.id
    
    if call.data == "sort_rating":
        sort_preference[chat_id] = "rating"
    elif call.data == "sort_date":
        sort_preference[chat_id] = "date"

    list_items(call.message)

def process_list(message,chat_id):
    if message.lower() == 'ігри':
        media_type[chat_id] = 'game'
    elif message.lower() == 'книги':
        media_type[chat_id] = 'book'
    print(media_type)
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


def send_paginated_list(chat_id, page,year=None, years=None, option=None, search_query=None):
    items_per_page = 80 # TODO: issue?
    if chat_id not in query_dict:
        query_dict[chat_id] = {}
    query = query_dict[chat_id] #TODO: implement rating and date sorting
    if option is not None:
       if option == 'rating':
            query[option] = search_query
       else:
            query[str(option)] = {'$regex': search_query, '$options': 'i'}
    elif year is not None:
        query['year'] = year
    elif years is not None:
        query['year'] = {'$in': years}
    if chat_id not in sort_preference:
        sort_preference[chat_id] = {}
    movie_type_value = movie_type.get(chat_id)
    print(movie_type_value)
    if 'date' in sort_preference[chat_id]:
        if 'book' in media_type[chat_id]:
            all_items = list(db.books.find(query).sort([('date', -1), ('title', 1)]))
        elif 'game' in media_type[chat_id]:
            all_items = list(db.games.find(query).sort([('date', -1), ('title', 1)]))
        elif 'film' in media_type[chat_id]:
            if movie_type_value in ['film', 'anime_series', 'anime_movie', 'series', 'animated_series', 'animated_movie'] :
                match_query = {'type': movie_type_value, **query}
            elif movie_type.get(chat_id) == 'anime':
                match_query = {'type': {'$in': ['anime_series', 'anime_movie']}, **query}
            elif movie_type.get(chat_id) == 'animated':
                match_query = {'type': {'$in': ['animated_series', 'animated_movie']}, **query}
            else:
                match_query = query
            all_items = list(db.films.aggregate([
                    {'$match': match_query},
                    {'$addFields': {
                        'sort_date': {
                            '$cond': {
                                'if': {'$eq': ['$date', 'None']},
                                'then': '0001-01-01',
                                'else': '$date'
                            }
                        }
                    }},
                    {'$sort': {'sort_date': -1, 'title': 1}},
                    {'$unset': 'sort_date'}
                ]))
    else:
        if 'book' in media_type[chat_id]:
            all_items = list(db.books.find(query).sort([('rating', -1), ('title', 1)]))
        elif 'game' in media_type[chat_id]:
            all_items = list(db.games.find(query).sort([('rating', -1), ('title', 1)]))
        elif 'film' in media_type[chat_id]:
            if movie_type_value in ['film', 'anime_series', 'anime_movie', 'series', 'animated_series', 'animated_movie']:
                match_query = {'type': movie_type_value, **query}
            elif movie_type.get(chat_id) == 'anime':
                match_query = {'type': {'$in': ['anime_series', 'anime_movie']}, **query}
            elif movie_type.get(chat_id) == 'animated':
                match_query = {'type': {'$in': ['animated_series', 'animated_movie']}, **query}
            else:
                match_query = query
            all_items = list(db.films.find(match_query).sort([('rating', -1), ('title', 1)]))
    total_pages = (len(all_items) + items_per_page - 1) // items_per_page
    start = page * items_per_page
    end = start + items_per_page
    items = all_items[start:end]

    markup = types.InlineKeyboardMarkup()
    for item in items:
        title = item.get('title', 'Немає назви')
        rating = item.get('rating', 'Немає оцінки')
        date = item.get('date', 'Немає дати')
        button_text = f"{title} | {rating}/10 | {date}"
        button = types.InlineKeyboardButton(text=button_text, callback_data=f"{media_type[chat_id]}_{item['_id']}")
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
    year = int(data[4]) if len(data) > 4 and data[4] != 'None' else None
    years = list(map(int, data[4].strip('[]').split(','))) if len(data) > 4 and data[4] != 'None' else None
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

@bot.callback_query_handler(func=lambda call: call.data.startswith(('film_', 'game_', 'book_')))
def send_media_info(call):
    chat_id = call.message.chat.id
    media_id = call.data.split('_')[1]
    media = db[media_type[chat_id] + 's'].find_one({'_id': ObjectId(media_id)})
    
    if media:
        markup = markup_buttons(chat_id, media_id, media)

        title = media.get('title', 'Немає назви')
        rating = media.get('rating', 'Немає оцінки')
        review = media.get('review', '-')
        year = media.get('year', 'Немає року')
        date = media.get('date', 'Немає дати')
        
        if media_type[chat_id] == 'film' or media_type[chat_id] == 'game':
            conditions = media.get('conditions', 'Немає умов')
        if media_type[chat_id] == 'film': 
            category = media.get('type', 'Тип не вказано') 
            # TODO: Change category to ukrainian
            
        if media_type[chat_id] == 'film':
            message_text = (f"Назва: {title}\n"
                            f"Оцінка: {rating}\n"
                            f"Відгук: {review}\n"
                            f"Рік: {year}\n"
                            f"Дата перегляду: {date}\n"
                            f"Умови перегляду: {conditions}\n"
                            f"Тип: {category}")
        elif media_type[chat_id] == 'game':
            message_text = (f"Назва: {title}\n"
                            f"Оцінка: {rating}\n"
                            f"Відгук: {review}\n"
                            f"Рік: {year}\n"
                            f"Дата: {date}\n"
                            f"Умови: {conditions}")
        elif media_type[chat_id] == 'book':
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
    media_id = call.data.split('_')[2]
    print(media_id)
    params_dict[chat_id] = {'media_id': media_id}
    db[media_type[chat_id] + 's'].delete_one({'_id': ObjectId(media_id)})
    if media_type[chat_id] == 'film': #TODO: Upgrade for anime, series
        msg = 'Фільм видалено.'
    elif media_type[chat_id] == 'game':
        msg = 'Гру видалено.'
    elif media_type[chat_id] == 'book':
        msg = 'Книгу видалено.'
    bot.send_message(chat_id, msg)

@bot.callback_query_handler(func=lambda call: call.data.startswith(('edit_film_', 'edit_game_', 'edit_book_')))
def edit_media(call):
    chat_id = call.message.chat.id
    media_id = call.data.split('_')[2]
    params_dict[chat_id] = {'media_id': media_id}
    options = {
        'Редагувати назву': {'callback_data': f'edit_title_{media_type[chat_id]}_{media_id}'},
        'Редагувати оцінку': {'callback_data': f'edit_rating_{media_type[chat_id]}_{media_id}'},
        'Редагувати відгук': {'callback_data': f'edit_review_{media_type[chat_id]}_{media_id}'},
        'Редагувати дату': {'callback_data': f'edit_date_{media_type[chat_id]}_{media_id}'},
        'Редагувати все': {'callback_data': f'edit_all_{media_type[chat_id]}_{media_id}'}
    }
    if media_type[chat_id] in ['film', 'game']:
        options['Редагувати умови'] = {'callback_data': f'edit_conditions_{media_type[chat_id]}_{media_id}'}
        if media_type[chat_id] == 'film':
            options['Редагувати тип'] = {'callback_data': f'edit_type_{media_type[chat_id]}_{media_id}'}
    elif media_type[chat_id] == 'book':
        options['Редагувати автора'] = {'callback_data': f'edit_author_{media_type[chat_id]}_{media_id}'}
    # TODO: Change position
    markup = quick_markup(options)
    bot.send_message(chat_id, f'Оберіть, що саме редагувати:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_'))
def edit_smth(call):
    chat_id = call.message.chat.id
    attribute, _, media_id = call.data.split('_')[1:] #TODO: refactor this
    params_dict[chat_id] = {'media_id': media_id, 'media_type': media_type[chat_id],'state': f'editing_{attribute}'} #TODO: refactor this?
    if attribute == 'title' or attribute == 'all':
        if media_type[chat_id] == 'film': 
            add_movie(call.message)
        elif media_type[chat_id] == 'game':
            add_game(call.message)
        elif media_type[chat_id] == 'book':
            add_book(call.message)
    elif attribute == 'rating':
        ask_for_rating(call.message)
    elif attribute == 'review':
        ask_for_review(call.message)
    elif attribute == 'date':
        ask_for_date(call.message)
    elif attribute == 'conditions':
        ask_for_conditions(call.message)
    elif attribute == 'author':
        ask_for_author(call.message)
    elif attribute == 'type':
        ask_for_type(call.message)
        
@bot.callback_query_handler(func=lambda call: call.data.startswith('back_to_list_'))
def back_to_list(call):
    message = Message(
        message_id=call.message.message_id,
        from_user=call.from_user,
        date=call.message.date,
        chat=call.message.chat,
        content_type='text',
        options={},
        json_string=None,
    )
    chat_id = call.message.chat.id
    if media_type.get(chat_id) is None:
        media_type[chat_id] = 'film'
    message.text = media_type[chat_id]  
    
    process_list(message.text,chat_id)