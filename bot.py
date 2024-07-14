from dotenv import load_dotenv
import os
import telebot
from telebot import types
from db import db
import datetime
from collections import defaultdict

load_dotenv() 

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

params_dict = defaultdict(dict)

@bot.message_handler(commands=['addmovie'])
def add_movie(message):
    msg = bot.send_message(message.chat.id, "Як називався фільм?")
    bot.register_next_step_handler(msg, process_title)

def process_title(message):
    params_dict[message.chat.id]['title'] = message.text
    ask_for_rating(message)

def ask_for_rating(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Оцінка фільму (або введи -, щоб пропустити"):')
    bot.register_next_step_handler(msg, process_rating)

def process_rating(message):
    if message.text.lower() != '-' and message.text.isnumeric() and 0 <= int(message.text) <= 10:
        rating = message.text+ '/10'
    else:
        rating = None
    params_dict[message.chat.id]['rating'] = rating
    ask_for_review(message)

def ask_for_review(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Відгук (або введи -, щоб пропустити"):')
    bot.register_next_step_handler(msg, process_review)

def process_review(message):
    review = message.text if message.text.lower() != 'skip' else None
    params_dict[message.chat.id]['review'] = review
    ask_for_date(message)

def ask_for_date(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = ['Сьогодні', 'Раніше', 'Невідомо']
    for option in options:
        markup.add(option)
    msg = bot.send_message(chat_id, 'Коли ти дивився фільм?', reply_markup=markup)
    bot.register_next_step_handler(msg, process_date)

def process_date(message):
    date = message.text
    if date == 'Сьогодні':
        full_date = datetime.datetime.now().strftime('%Y-%m-%d')
        year = datetime.datetime.now().year
    elif date == 'Раніше': #TODO: Does it work?
        msg = bot.send_message(message.chat.id, 'Введи дату у форматі рік-місяць-день:')
        bot.register_next_step_handler(msg, process_custom_date)
        return
    else:
        full_date = None
        year = None
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
    params_dict[message.chat.id]['full_date'] = full_date
    params_dict[message.chat.id]['year'] = year
    ask_for_conditions(message)

def ask_for_conditions(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = ['Сам вдома', 'З кимось вдома', 'На великих екранах', 'Невідомо', 'Інше']
    for option in options:
        markup.add(option)
    msg = bot.send_message(chat_id, 'Як ти дивився фільм?', reply_markup=markup)
    bot.register_next_step_handler(msg, process_conditions)

def process_conditions(message):
    conditions = message.text
    if conditions == 'Інше':
        process_custom_conditions(message)
        return
    params_dict[message.chat.id]['conditions'] = conditions
    save_movie_info(message)

def process_custom_conditions(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = ['З кимось, а потім сам', 'Сам, а потім з кимось']
    for option in options:
        markup.add(option)
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



@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['addbook'])
def add_book(message):
    bot.reply_to(message, "What is the title of the book?")
    bot.register_next_step_handler(message, add_book_title)



# @bot.message_handler(func=lambda msg: True)
# def echo_all(message):    
#     bot.reply_to(message, message.text)

bot.infinity_polling()

def add_book_title(message):
    book_title = message.text
    bot.reply_to(message, f"Book title is {book_title}")

