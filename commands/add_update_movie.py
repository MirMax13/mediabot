import datetime
from bson import ObjectId
from telebot import types
from db import db
from config import bot, params_dict

def add_movie(message):
    msg = bot.send_message(message.chat.id, "Як називався фільм?")
    bot.register_next_step_handler(msg, process_title)

def process_title(message):
    chat_id = message.chat.id
    if 'state' in params_dict[chat_id] and params_dict[chat_id]['state'] == 'editing_title':
        new_title = message.text
        film_id = params_dict[chat_id]['film_id']
        db.films.update_one({'_id': ObjectId(film_id)}, {'$set': {'title': new_title}})
        bot.send_message(chat_id, f"Назву фільму змінено на '{new_title}'")
        params_dict[chat_id] = {}
    else:
        params_dict[message.chat.id]['title'] = message.text
        ask_for_rating(message)

def ask_for_rating(message):
    msg = bot.send_message(message.chat.id, 'Оцінка фільму (або введи -, щоб пропустити"):')
    bot.register_next_step_handler(msg, process_rating)

def process_rating(message):
    try:
        if message.text.lower() != '-':
            rating = float(message.text)
            if 0 <= rating <= 10:
                    rating = f"{rating}/10"
            else:
                rating = None
        else:
            rating = None
    except ValueError:
        rating = None
    if 'state' in params_dict[message.chat.id] and params_dict[message.chat.id]['state'] == 'editing_rating':
        film_id = params_dict[message.chat.id]['film_id']
        db.films.update_one({'_id': ObjectId(film_id)}, {'$set': {'rating': rating}})
        bot.send_message(message.chat.id, f"Оцінку фільму змінено на '{rating}'")
        params_dict[message.chat.id] = {}
    else:
        params_dict[message.chat.id]['rating'] = rating
        ask_for_review(message)

def ask_for_review(message):
    msg = bot.send_message(message.chat.id, 'Відгук (або введи -, щоб пропустити"):')
    bot.register_next_step_handler(msg, process_review)

def process_review(message):
    review = message.text if message.text.lower() != 'skip' else None
    if 'state' in params_dict[message.chat.id] and params_dict[message.chat.id]['state'] == 'editing_review':
        film_id = params_dict[message.chat.id]['film_id']
        db.films.update_one({'_id': ObjectId(film_id)}, {'$set': {'review': review}})
        bot.send_message(message.chat.id, f"Відгук змінено на '{review}'")
        params_dict[message.chat.id] = {}
    else:
        params_dict[message.chat.id]['review'] = review
        ask_for_date(message)

def ask_for_date(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = ['Сьогодні', 'Раніше', 'Невідомо']
    for option in options:
        markup.add(option)
    msg = bot.send_message(message.chat.id, 'Коли ти дивився фільм? Вибери кнопку', reply_markup=markup)
    bot.register_next_step_handler(msg, process_date)

def process_date(message):
    date = message.text
    if date == 'Сьогодні':
        full_date = datetime.datetime.now().strftime('%Y-%m-%d')
        year = datetime.datetime.now().year
    elif date == 'Раніше':
        msg = bot.send_message(message.chat.id, 'Введи дату у форматі рік-місяць-день:')
        bot.register_next_step_handler(msg, process_custom_date)
        return
    else:
        full_date = None
        year = None

    if 'state' in params_dict[message.chat.id] and params_dict[message.chat.id]['state'] == 'editing_date':
        film_id = params_dict[message.chat.id]['film_id']
        db.films.update_one({'_id': ObjectId(film_id)}, {'$set': {'date_watched': full_date}})
        bot.send_message(message.chat.id, f"Дата перегляду змінена на '{full_date}'")
        params_dict[message.chat.id] = {}
    else:
        params_dict[message.chat.id]['full_date'] = full_date
        params_dict[message.chat.id]['year'] = year
        ask_for_conditions(message)

def process_custom_date(message):
    try:
        if len(message.text) == 4:  # Only year
            full_date = f"{message.text}"
            year = int(message.text)
        elif len(message.text) == 7:  # Year and month
            full_date = f"{message.text}"
            year = int(message.text[:4])
        else:
            full_date = datetime.datetime.strptime(message.text, '%Y-%m-%d').strftime('%Y-%m-%d')
            year = datetime.datetime.strptime(message.text, '%Y-%m-%d').year
    except ValueError:
        bot.send_message(message.chat.id, 'Неправильний формат дати. Спробуй ще раз')
        ask_for_date(message)
        return
    if 'state' in params_dict[message.chat.id] and params_dict[message.chat.id]['state'] == 'editing_date':
        film_id = params_dict[message.chat.id]['film_id']
        db.films.update_one({'_id': ObjectId(film_id)}, {'$set': {'date_watched': full_date}})
        bot.send_message(message.chat.id, f"Дата перегляду змінена на '{full_date}'")
        params_dict[message.chat.id] = {}
    else:
        params_dict[message.chat.id]['full_date'] = full_date
        params_dict[message.chat.id]['year'] = year
        ask_for_conditions(message)

def ask_for_conditions(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = ['Сам вдома', 'З кимось вдома', 'На великих екранах', 'Невідомо', 'Інше']
    for option in options:
        markup.add(option)
    msg = bot.send_message(message.chat.id, 'Як ти дивився фільм?', reply_markup=markup)
    bot.register_next_step_handler(msg, process_conditions)

def process_conditions(message):
    conditions = message.text
    chat_id = message.chat.id
    if conditions == 'Інше':
        ask_for_custom_conditions(message)
        return
    params_dict[chat_id]['conditions'] = conditions
    if 'state' in params_dict[chat_id]:
        if params_dict[chat_id]['state'] == 'editing_all':
            update_movie_info(message)
        else:
            film_id = params_dict[chat_id]['film_id']
            db.films.update_one({'_id': ObjectId(film_id)}, {'$set': {'watch_conditions': conditions}})
            bot.send_message(chat_id, f"Умови перегляду змінено на '{conditions}'")
            params_dict[chat_id] = {}
    else:
        save_movie_info(message)

def ask_for_custom_conditions(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = ['З кимось, а потім сам', 'Сам, а потім з кимось', 'Недодивився']
    for option in options:
        markup.add(option)
    msg = bot.send_message(chat_id, 'Оберіть умови перегляду:', reply_markup=markup)
    bot.register_next_step_handler(msg, process_custom_conditions)
    
def process_custom_conditions(message):
    chat_id = message.chat.id
    custom_conditions = message.text
    params_dict[chat_id]['conditions'] = custom_conditions
    if 'film_id' in params_dict[chat_id]:
        if params_dict[chat_id]['state'] == 'editing_all':
            update_movie_info(message)
        else:
            film_id = params_dict[chat_id]['film_id']
            db.films.update_one({'_id': ObjectId(film_id)}, {'$set': {'watch_conditions': custom_conditions}})
            bot.send_message(chat_id, f"Умови перегляду змінено на '{custom_conditions}'")
            params_dict[chat_id] = {}
    else:
        save_movie_info(message) #TODO: Does it work?
    
def save_movie_info(message):
    if message.chat.id not in params_dict:
        params_dict[message.chat.id] = {}
    
    db.films.insert_one({
        'title': params_dict[message.chat.id]['title'],
        'rating': params_dict[message.chat.id]['rating'],
        'review': params_dict[message.chat.id]['review'],
        'year':  params_dict[message.chat.id]['year'],
        'date_watched': params_dict[message.chat.id]['full_date'],
        'watch_conditions': params_dict[message.chat.id]['conditions']
    })
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Фільм успішно додано!', reply_markup=types.ReplyKeyboardRemove())

def update_movie_info(message):
    chat_id = message.chat.id
    film_id = params_dict[chat_id]['film_id']
    title = params_dict[chat_id].get('title')
    rating = params_dict[chat_id].get('rating')
    review = params_dict[chat_id].get('review')
    full_date = params_dict[chat_id].get('full_date')
    year = params_dict[chat_id].get('year')
    conditions = params_dict[chat_id].get('conditions')

    update_data = {}
    if title:
        update_data['title'] = title
    if rating:
        update_data['rating'] = rating
    if review:
        update_data['review'] = review
    if full_date:
        update_data['date_watched'] = full_date
    if year:
        update_data['year'] = year
    if conditions:
        update_data['watch_conditions'] = conditions

    db.films.update_one({'_id': ObjectId(film_id)}, {'$set': update_data})
    bot.send_message(chat_id, 'Інформацію про фільм оновлено.', reply_markup=types.ReplyKeyboardRemove())