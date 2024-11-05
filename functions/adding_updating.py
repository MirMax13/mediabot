import datetime
from bson import ObjectId
from telebot import types
from db import db
from config import bot, params_dict
from functions.admin_check import is_user_admin
import os
from variables.globals import media_type

MAX_RECORDS_PER_USER = int(os.getenv('MAX_RECORDS_PER_USER', 300))
messages = {
    'film': {
        'editing': {
            'date': "Коли ти дивився цей контент? Вибери кнопку"
        },
        'adding': "Контент"
    },
    'game': {
        'editing': {
            'date': "Коли ти грав/дивився гру? Вибери кнопку"
        },
        'adding':"Гру"
    },
    'book': {
        'editing': {
            'date': "Коли ти читав книгу? Вибери кнопку"
        },
        'adding': "Книгу",
    }
}

def add_back_button(markup, media_id,chat_id):
    button = types.InlineKeyboardButton(text="Назад", callback_data=f"{media_type[chat_id]}_{media_id}")
    markup.add(button)

def process_title(message):
    chat_id = message.chat.id
    if 'state' in params_dict[chat_id] and params_dict[chat_id]['state'] == 'editing_title':
        title = message.text
        media_id = params_dict[chat_id]['media_id']
        db[media_type[chat_id] + 's'].update_one({'_id': ObjectId(media_id)}, {'$set': {'title': title}})
        markup = types.InlineKeyboardMarkup()
        add_back_button(markup, media_id,chat_id)
        
        bot.send_message(chat_id, f"Назву змінено на '{title}'",reply_markup=markup)
        params_dict[chat_id] = {}

    else:
        params_dict[chat_id]['title'] = message.text
        if media_type[chat_id] == 'book':
            ask_for_author(message)
        else:
            ask_for_rating(message)

def ask_for_author(message):
    msg = bot.send_message(message.chat.id, 'Автор (або введи -, щоб пропустити"):')
    bot.register_next_step_handler(msg, process_author)

def process_author(message):
    author = message.text if message.text.lower() != '-' else None
    chat_id = message.chat.id
    if 'state' in params_dict[chat_id] and params_dict[chat_id]['state'] == 'editing_author':
        media_id = params_dict[chat_id]['media_id']
        db[media_type[chat_id] + 's'].update_one({'_id': ObjectId(media_id)}, {'$set': {'author': author}})
        markup = types.InlineKeyboardMarkup()
        add_back_button(markup, media_id,chat_id)
        bot.send_message(chat_id, f"Автора змінено на '{author}'", reply_markup=markup)
        params_dict[chat_id] = {}
    else:
        params_dict[chat_id]['author'] = author
        ask_for_rating(message)


def ask_for_rating(message):
    msg = bot.send_message(message.chat.id, 'Оцінка (або введи -, щоб пропустити"):')
    bot.register_next_step_handler(msg, process_rating)

def process_rating(message):
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
        db[media_type[chat_id] + 's'].update_one({'_id': ObjectId(media_id)}, {'$set': {'rating': rating}})
        markup = types.InlineKeyboardMarkup()
        add_back_button(markup, media_id,chat_id)
        bot.send_message(chat_id, f"Оцінку змінено на '{rating}'", reply_markup=markup)
        params_dict[chat_id] = {}
    else:
        params_dict[chat_id]['rating'] = rating
        ask_for_review(message,)

def ask_for_review(message):
    msg = bot.send_message(message.chat.id, 'Відгук (або введи -, щоб пропустити"):')
    bot.register_next_step_handler(msg, process_review)

def process_review(message):
    chat_id = message.chat.id
    review = message.text if message.text.lower() != 'skip' else None
    if 'state' in params_dict[chat_id] and params_dict[chat_id]['state'] == 'editing_review':
        media_id = params_dict[chat_id]['media_id']
        db[media_type[chat_id] + 's'].update_one({'_id': ObjectId(media_id)}, {'$set': {'review': review}})
        markup = types.InlineKeyboardMarkup()
        add_back_button(markup, media_id,chat_id)
        bot.send_message(chat_id, f"Відгук змінено на '{review}'", reply_markup=markup)
        params_dict[chat_id] = {}
    else:
        params_dict[chat_id]['review'] = review
        ask_for_date(message)

def ask_for_date(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = ['Сьогодні', 'Раніше', 'Невідомо']
    for option in options:
        markup.add(option)
    msg = bot.send_message(chat_id, messages[media_type[chat_id]]['editing']['date'], reply_markup=markup)
    bot.register_next_step_handler(msg, process_date)

def process_date(message):
    date = message.text
    chat_id = message.chat.id
    if date == 'Сьогодні':
        full_date = datetime.datetime.now().strftime('%Y-%m-%d')
        year = datetime.datetime.now().year
    elif date == 'Раніше':
        msg = bot.send_message(chat_id, 'Введи дату у форматі рік-місяць-день:')
        bot.register_next_step_handler(msg, process_custom_date)
        return
    else:
        full_date = None
        year = None

    if 'state' in params_dict[chat_id] and params_dict[chat_id]['state'] == 'editing_date':
        media_id = params_dict[chat_id]['media_id']
        db[media_type[chat_id] + 's'].update_one({'_id': ObjectId(media_id)}, {'$set': {'date': full_date}})
        markup = types.InlineKeyboardMarkup()
        add_back_button(markup, media_id,chat_id)
        bot.send_message(chat_id, f"Дата змінена на '{full_date}'", reply_markup=markup)
        params_dict[chat_id] = {}
    else:
        params_dict[chat_id]['full_date'] = full_date
        params_dict[chat_id]['year'] = year
        if media_type[chat_id] == 'book':
            if 'state' in params_dict[chat_id] and params_dict[chat_id]['state'] == 'editing_all':
                update_info(message)
            else:
                save_info(message)
        else:
            ask_for_conditions(message)

def process_custom_date(message):
    chat_id = message.chat.id
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
        bot.send_message(chat_id, 'Неправильний формат дати. Спробуй ще раз')
        ask_for_date(message)
        return
    if 'state' in params_dict[chat_id] and params_dict[chat_id]['state'] == 'editing_date':
        media_id = params_dict[chat_id]['media_id']
        print("media_id: ", media_id)
        db[media_type[chat_id] + 's'].update_one({'_id': ObjectId(media_id)}, {'$set': {'date': full_date}})
        markup = types.InlineKeyboardMarkup()
        add_back_button(markup, media_id,chat_id)
        bot.send_message(chat_id, f"Дата змінена на '{full_date}'", reply_markup=markup)
        params_dict[chat_id] = {}
    else:
        params_dict[chat_id]['full_date'] = full_date
        params_dict[chat_id]['year'] = year
        if media_type[chat_id] == 'book':
            if 'state' in params_dict[chat_id] and params_dict[chat_id]['state'] == 'editing_all':
                update_info(message)
            else:
                save_info(message)
        else:
            ask_for_conditions(message)

def ask_for_conditions(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    if media_type[chat_id] == 'film':
        options = ['Сам вдома', 'З кимось вдома', 'На великих екранах', 'Невідомо', 'Інше']
    elif media_type[chat_id] == 'game':
        options = ['Пройшов', 'Подивився', 'Грав', 'Дивився', 'Невідомо']
    for option in options:
        markup.add(option)
    if media_type[chat_id] == 'film':
        msg = bot.send_message(chat_id, 'Як ти дивився фільм?', reply_markup=markup)
    elif media_type[chat_id] == 'game':
        msg = bot.send_message(chat_id, 'Грав/дивився?', reply_markup=markup)
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
            update_info(message)
        else:
            media_id = params_dict[chat_id]['media_id']
            db[media_type[chat_id] + 's'].update_one({'_id': ObjectId(media_id)}, {'$set': {'conditions': conditions}})
            markup = types.InlineKeyboardMarkup()
            add_back_button(markup, media_id,chat_id)
            bot.send_message(chat_id, f"Умови перегляду змінено на '{conditions}'", reply_markup=markup)
            params_dict[chat_id] = {}
    else:
        save_info(message)

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
    if 'media_id' in params_dict[chat_id]:
        if params_dict[chat_id]['state'] == 'editing_all':
            update_info(message)
        else:
            media_id = params_dict[chat_id]['media_id']
            db[media_type[chat_id] + 's'].update_one({'_id': ObjectId(media_id)}, {'$set': {'conditions': custom_conditions}})
            markup = types.InlineKeyboardMarkup()
            add_back_button(markup, media_id,chat_id)
            bot.send_message(chat_id, f"Умови перегляду змінено на '{custom_conditions}'", reply_markup=markup)
            params_dict[chat_id] = {}
    else:
        save_info(message)
    
def save_info(message):
    chat_id = message.chat.id
    if chat_id not in params_dict:
        params_dict[chat_id] = {}
    
    total_records = (
        db.films.count_documents({'user_id': chat_id}) +
        db.books.count_documents({'user_id': chat_id}) +
        db.games.count_documents({'user_id': chat_id})
    )
    
    if (total_records >= MAX_RECORDS_PER_USER) and not is_user_admin(message):
        bot.send_message(chat_id, 'Ви досягли ліміту записів. Видаліть деякі записи, щоб додати нові.')
        return
    
    media_data = {
        'user_id': chat_id,
        'title': params_dict[chat_id]['title'],
        'rating': params_dict[chat_id]['rating'],
        'review': params_dict[chat_id]['review'],
        'year':  params_dict[chat_id]['year'],
        'date': params_dict[chat_id]['full_date']
    }
    if media_type[chat_id] in ['film', 'game']:
        media_data['conditions'] = params_dict[chat_id]['conditions']
    elif media_type[chat_id] == 'book':
        media_data['author'] = params_dict[chat_id]['author']
    db[media_type[chat_id] + 's'].insert_one(media_data)
    msg = messages[media_type[chat_id]]['adding']+ ' успішно додано!'
    bot.send_message(chat_id, msg, reply_markup=types.ReplyKeyboardRemove())

def update_info(message):
    chat_id = message.chat.id
    media_id = params_dict[chat_id]['media_id']
    title = params_dict[chat_id].get('title')
    rating = params_dict[chat_id].get('rating')
    review = params_dict[chat_id].get('review')
    full_date = params_dict[chat_id].get('full_date')
    year = params_dict[chat_id].get('year')
    conditions = params_dict[chat_id].get('conditions')
    author = params_dict[chat_id].get('author')

    update_data = {}
    if title:
        update_data['title'] = title
    if rating:
        update_data['rating'] = rating
    if review:
        update_data['review'] = review
    if full_date:
        update_data['date'] = full_date
    if year:
        update_data['year'] = year

    if media_type[chat_id] in ['film', 'game'] and conditions:
        update_data['conditions'] = conditions
    elif media_type[chat_id] == 'book' and author:
        update_data['author'] = author

    db[media_type[chat_id] + 's'].update_one({'_id': ObjectId(media_id)}, {'$set': update_data})
    bot.send_message(chat_id, 'Інформацію оновлено.', reply_markup=types.ReplyKeyboardRemove())
