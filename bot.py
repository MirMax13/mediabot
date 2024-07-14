from dotenv import load_dotenv
import os
import telebot
from telebot import types
from db import db
import date
load_dotenv() 

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}

def start_add_movie(message):
    user_data[message.chat.id] = {'title': None, 'rating': None, 'review': None, 'date_watched': None, 'watch_conditions': None}
    msg = bot.send_message(message.chat.id, "What is the title of the movie?")
    bot.register_next_step_handler(msg, ask_for_rating)


def ask_for_rating(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Enter the rating (or skip this step by typing "skip"):')
    bot.register_next_step_handler(msg, ask_for_review, movie_title=message.text)

def ask_for_review(message, movie_title):
    if message.text.lower() != 'skip':
        rating = message.text+ '/10'
    else:
        rating = None
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Enter the review (or skip this step by typing "skip"):')
    bot.register_next_step_handler(msg, ask_for_date, movie_title=movie_title, rating=rating)

def ask_for_date(message, movie_title, rating):
    review = message.text if message.text.lower() != 'skip' else None
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = ['Сьогодні', 'Раніше', 'Невідомо']
    for option in options:
        markup.add(option)
    msg = bot.send_message(chat_id, 'When did you watch the movie?', reply_markup=markup)
    bot.register_next_step_handler(msg, ask_for_conditions, movie_title=movie_title, rating=rating, review=review)

def ask_for_conditions(message, movie_title, rating, review):
    date = message.text
    if date == 'Сьогодні':
        date = date.today()
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = ['Alone at home', 'With someone at home', 'On a screen with others', 'Unknown', 'Other']
    for option in options:
        markup.add(option)
    msg = bot.send_message(chat_id, 'How did you watch the movie?', reply_markup=markup)
    bot.register_next_step_handler(msg, save_movie_info, movie_title=movie_title, rating=rating, review=review, date_watched=date)

def save_movie_info(message, movie_title, rating, review, date_watched):
    conditions = message.text
    db.films.insert_one({
        'title': movie_title,
        'rating': rating,
        'review': review,
        'date_watched': date_watched,
        'watch_conditions': conditions
    })
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Film added successfully!', reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['addbook'])
def add_book(message):
    bot.reply_to(message, "What is the title of the book?")
    bot.register_next_step_handler(message, add_book_title)

@bot.message_handler(commands=['addmovie'])
def add_movie(message):
    msg = bot.send_message(message.chat.id, "What is the title of the movie?")
    bot.register_next_step_handler(msg, ask_for_rating)

# @bot.message_handler(func=lambda msg: True)
# def echo_all(message):    
#     bot.reply_to(message, message.text)

bot.infinity_polling()

def add_book_title(message):
    book_title = message.text
    bot.reply_to(message, f"Book title is {book_title}")

