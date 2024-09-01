import datetime
from bson import ObjectId
from telebot import types
from db import db
from config import bot, params_dict

def process_title(message,media_type):
    chat_id = message.chat.id
    if 'state' in params_dict[chat_id] and params_dict[chat_id]['state'] == 'editing_title':
        new_title = message.text
        media_id = params_dict[chat_id]['media_id']
        db[media_type + 's'].update_one({'_id': ObjectId(media_id)}, {'$set': {'title': new_title}})
        bot.send_message(chat_id, f"Назву змінено на '{new_title}'")
        params_dict[chat_id] = {}
    else:
        params_dict[message.chat.id]['title'] = message.text
        ask_for_rating(message, media_type)

def ask_for_rating(message, media_type):
    msg = bot.send_message(message.chat.id, 'Оцінка (або введи -, щоб пропустити"):')
    bot.register_next_step_handler(msg, process_rating, media_type)

def process_rating(message, media_type):
    try:
        if message.text.lower() != '-':
            rating = float(message.text)
            if 0 <= rating <= 10:
                    rating = round(rating, 1)
            else:
                rating = None
        else:
            rating = None
    except ValueError:
        rating = None
    chat_id = message.chat.id
    if 'state' in params_dict[chat_id] and params_dict[chat_id]['state'] == 'editing_rating':
        media_id = params_dict[chat_id]['media_id']
        db[media_type + 's'].update_one({'_id': ObjectId(media_id)}, {'$set': {'rating': rating}})
        bot.send_message(chat_id, f"Оцінку змінено на '{rating}'")
        params_dict[chat_id] = {}
    else:
        params_dict[chat_id]['rating'] = rating
        ask_for_review(message, media_type)

def ask_for_review(message, media_type):
    msg = bot.send_message(message.chat.id, 'Відгук (або введи -, щоб пропустити"):')
    bot.register_next_step_handler(msg, process_review, media_type)

def process_review(message, media_type):
    review = message.text if message.text.lower() != 'skip' else None
    if 'state' in params_dict[message.chat.id] and params_dict[message.chat.id]['state'] == 'editing_review':
        media_id = params_dict[message.chat.id]['media_id']
        db[media_type + 's'].update_one({'_id': ObjectId(media_id)}, {'$set': {'review': review}})
        bot.send_message(message.chat.id, f"Відгук змінено на '{review}'")
        params_dict[message.chat.id] = {}
    else:
        params_dict[message.chat.id]['review'] = review
        ask_for_date(message, media_type)

def ask_for_date(message, media_type):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = ['Сьогодні', 'Раніше', 'Невідомо']
    for option in options:
        markup.add(option)
    if media_type == 'film':
        msg = bot.send_message(message.chat.id, 'Коли ти дивився фільм? Вибери кнопку', reply_markup=markup)
    elif media_type == 'game':
        msg = bot.send_message(message.chat.id, 'Коли ти грав/дивився гру? Вибери кнопку', reply_markup=markup)
    bot.register_next_step_handler(msg, process_date, media_type)

def process_date(message, media_type):
    date = message.text
    if date == 'Сьогодні':
        full_date = datetime.datetime.now().strftime('%Y-%m-%d')
        year = datetime.datetime.now().year
    elif date == 'Раніше':
        msg = bot.send_message(message.chat.id, 'Введи дату у форматі рік-місяць-день:')
        bot.register_next_step_handler(msg, process_custom_date, media_type)
        return
    else:
        full_date = None
        year = None

    if 'state' in params_dict[message.chat.id] and params_dict[message.chat.id]['state'] == 'editing_date':
        media_id = params_dict[message.chat.id]['media_id']
        db[media_type + 's'].update_one({'_id': ObjectId(media_id)}, {'$set': {'date': full_date}})
        bot.send_message(message.chat.id, f"Дата змінена на '{full_date}'")
        params_dict[message.chat.id] = {}
    else:
        params_dict[message.chat.id]['full_date'] = full_date
        params_dict[message.chat.id]['year'] = year
        ask_for_conditions(message, media_type)

def process_custom_date(message, media_type):
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
        ask_for_date(message, media_type)
        return
    if 'state' in params_dict[message.chat.id] and params_dict[message.chat.id]['state'] == 'editing_date':
        media_id = params_dict[message.chat.id]['media_id']
        db[media_type + 's'].update_one({'_id': ObjectId(media_id)}, {'$set': {'date': full_date}})
        bot.send_message(message.chat.id, f"Дата змінена на '{full_date}'")
        params_dict[message.chat.id] = {}
    else:
        params_dict[message.chat.id]['full_date'] = full_date
        params_dict[message.chat.id]['year'] = year
        ask_for_conditions(message, media_type)

def ask_for_conditions(message, media_type):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    if media_type == 'film':
        options = ['Сам вдома', 'З кимось вдома', 'На великих екранах', 'Невідомо', 'Інше']
    elif media_type == 'game':
        options = ['Пройшов', 'Подивився', 'Грав', 'Дивився', 'Невідомо']
    for option in options:
        markup.add(option)
    if media_type == 'film':
        msg = bot.send_message(message.chat.id, 'Як ти дивився фільм?', reply_markup=markup)
    elif media_type == 'game':
        msg = bot.send_message(message.chat.id, 'Грав/дивився?', reply_markup=markup)
    bot.register_next_step_handler(msg, process_conditions, media_type)

def process_conditions(message, media_type):
    conditions = message.text
    chat_id = message.chat.id
    if conditions == 'Інше':
        ask_for_custom_conditions(message, media_type)
        return
    params_dict[chat_id]['conditions'] = conditions
    if 'state' in params_dict[chat_id]:
        if params_dict[chat_id]['state'] == 'editing_all':
            update_info(message, media_type)
        else:
            media_id = params_dict[chat_id]['media_id']
            db[media_type + 's'].update_one({'_id': ObjectId(media_id)}, {'$set': {'conditions': conditions}})
            params_dict[chat_id] = {}
    else:
        save_info(message, media_type)

def ask_for_custom_conditions(message, media_type):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = ['З кимось, а потім сам', 'Сам, а потім з кимось', 'Недодивився']
    for option in options:
        markup.add(option)
    msg = bot.send_message(chat_id, 'Оберіть умови перегляду:', reply_markup=markup)
    bot.register_next_step_handler(msg, process_custom_conditions, media_type)
    
def process_custom_conditions(message, media_type):
    chat_id = message.chat.id
    custom_conditions = message.text
    params_dict[chat_id]['conditions'] = custom_conditions
    if 'film_id' in params_dict[chat_id]:
        if params_dict[chat_id]['state'] == 'editing_all':
            update_info(message, media_type)
        else:
            film_id = params_dict[chat_id]['film_id']
            db.films.update_one({'_id': ObjectId(film_id)}, {'$set': {'conditions': custom_conditions}})
            bot.send_message(chat_id, f"Умови перегляду змінено на '{custom_conditions}'")
            params_dict[chat_id] = {}
    else:
        save_info(message, media_type) #TODO: Does it work?
    
def save_info(message, media_type):
    if message.chat.id not in params_dict:
        params_dict[message.chat.id] = {}
    
    db[media_type + 's'].insert_one({
        'title': params_dict[message.chat.id]['title'],
        'rating': params_dict[message.chat.id]['rating'],
        'review': params_dict[message.chat.id]['review'],
        'year':  params_dict[message.chat.id]['year'],
        'date': params_dict[message.chat.id]['full_date'],
        'conditions': params_dict[message.chat.id]['conditions']
    })
    chat_id = message.chat.id
    bot.send_message(chat_id, f'{media_type} успішно додано!', reply_markup=types.ReplyKeyboardRemove())

def update_info(message, media_type):
    chat_id = message.chat.id
    media_id = params_dict[chat_id]['media_id']
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
        if media_type == 'film':
            update_data['date'] = full_date
        elif media_type == 'game':
            update_data['date'] = full_date
    if year:
        update_data['year'] = year
    if conditions:
        update_data['conditions'] = conditions

    db[media_type + 's'].update_one({'_id': ObjectId(media_id)}, {'$set': update_data})
    bot.send_message(chat_id, 'Інформацію оновлено.', reply_markup=types.ReplyKeyboardRemove())