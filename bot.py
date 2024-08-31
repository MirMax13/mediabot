from dotenv import load_dotenv
import os
import telebot
from telebot import types
from telebot.util import quick_markup
from db import db
import datetime
from collections import defaultdict
from bson import ObjectId

load_dotenv() 

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

params_dict = defaultdict(dict)

@bot.message_handler(commands=['addmovie'])
def add_movie(message):
    msg = bot.send_message(message.chat.id, "Як називався фільм?")
    bot.register_next_step_handler(msg, process_title)

def process_title(message):
    chat_id = message.chat.id
    if 'state' in params_dict[chat_id] and params_dict[chat_id]['state'] == 'editing_title':
        new_title = message.text
        film_id = params_dict[chat_id]['film_id']
        # params_dict[chat_id]['title'] = new_title
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
    msg = bot.send_message(message.chat.id, 'Коли ти дивився фільм?', reply_markup=markup)
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
    options = ['З кимось, а потім сам', 'Сам, а потім з кимось']
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


@bot.message_handler(commands=['start', 'hello']) # TODO: fix using command while adding/editing
def send_welcome(message):
    if message.chat.id in params_dict and params_dict[message.chat.id]:
        bot.reply_to(message, "Ви вже виконуєте іншу команду. Завершіть її перед тим, як почати нову.")
    else:
        bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['addbook'])
def add_book(message):
    bot.reply_to(message, "What is the title of the book?")
    bot.register_next_step_handler(message, add_book_title)



# @bot.message_handler(func=lambda msg: True)
# def echo_all(message):    
#     bot.reply_to(message, message.text)



def add_book_title(message):
    book_title = message.text
    bot.reply_to(message, f"Book title is {book_title}")

@bot.message_handler(commands=['list'])
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
        all_items = db.films.find().sort('date_watched', 1)
        markup = types.InlineKeyboardMarkup()

        for item in all_items:
            title = item.get('title', 'Немає назви')
            button = types.InlineKeyboardButton(text=title, callback_data=f"film_{item['_id']}")
            markup.add(button)
        bot.send_message(chat_id, 'Оберіть фільм:', reply_markup=markup)
    elif list_type == 'За роком':
        msg = bot.send_message(chat_id, 'Введи рік:')
        bot.register_next_step_handler(msg, process_year)
    else:
        msg = bot.send_message(chat_id, 'Введи рік:')
        bot.register_next_step_handler(msg, process_years)

@bot.callback_query_handler(func=lambda call: call.data.startswith('film_'))
def send_film_info(call):
    chat_id = call.message.chat.id
    film_id = call.data.split('_')[1]
    film = db.films.find_one({'_id': ObjectId(film_id)})
    if film:
        markup = quick_markup({
            'Назад': {'callback_data': 'back_to_list'},
            'Редагувати': {'callback_data': f'edit_film_{film_id}'}
        })

        title = film.get('title', 'Немає назви')
        rating = film.get('rating', 'Немає оцінки')
        review = film.get('review', 'Немає відгуку')
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
        'Редагувати умови перегляду': {'callback_data': f'edit_conditions_{film_id}'},
        'Редагувати все': {'callback_data': f'edit_all_{film_id}'}
    })
    bot.send_message(chat_id, f'Оберіть, що саме редагувати:{film_id}', reply_markup=markup)

# @bot.callback_query_handler(func=lambda call: call.data.startswith('edit_all_'))
# def edit_all(call):
#     chat_id = call.message.chat.id
#     film_id = call.data.split('_')[2]
#     params_dict[chat_id] = {'film_id': film_id}
#     msg = bot.send_message(chat_id, f'Введи нову назву фільму:{film_id}')
#     bot.register_next_step_handler(msg, process_title)

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
    chat_id = call.message.chat.id
    all_items = db.films.find().sort('date_watched', 1)
    markup = telebot.types.InlineKeyboardMarkup()

    for item in all_items:
        title = item.get('title', 'Немає назви')
        button = telebot.types.InlineKeyboardButton(text=title, callback_data=f"film_{item['_id']}")
        markup.add(button)
    bot.send_message(chat_id, 'Оберіть фільм:', reply_markup=markup)


def process_year(message):
    chat_id = message.chat.id
    year = message.text
    bot.send_message(chat_id, f'Обраний рік: {year}')
    items = db.films.find({'year': year})
    for item in items:
        bot.send_message(chat_id, item)

def process_years(message):
    chat_id = message.chat.id
    years = message.text.split()
    bot.send_message(chat_id, f'Обрані роки: {years}')  # Діагностичне повідомлення
    items = db.films.find({'year': {'$in': years}})
    for item in items:
        bot.send_message(chat_id, item)

bot.infinity_polling()