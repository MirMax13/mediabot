import re
from config import bot
from db import db
from functions.admin_check import is_user_admin

def add_many_movies(message):
    chat_id = message.chat.id
    if not is_user_admin(message):
        bot.send_message(chat_id, "Ви не адміністратор")
        return
    bot.send_message(chat_id, 'Введи текстом увесь вміст файлу за певний рік')
    bot.register_next_step_handler(message, process_many_movies)

def process_many_movies(message):
    chat_id = message.chat.id
    text = message.text
    lines = text.split('\n')

    year = lines[0].strip()
    if year == "Невідомо":
        year_int = None
    else:
        try:
            year_int = int(year)
        except ValueError:
            bot.send_message(chat_id, 'Невірний формат року. Введіть, будь ласка, рік у форматі чисел.')
            return
    
    for line in lines[1:]:
        if not line.strip():
            continue
        try:
            # match = re.match(r'(.+?)\s*(\d{1,2}\.\d{1,2})?\s*(\d{1,1,2}\.\d/10)?\s*([+\-]+)?', line)
            match = re.match( 
                r'^(.+?)'                      # Назва фільму (захоплює все до дати, рейтингу або умов перегляду)
                r'(?:\s+(\d{1,2}\.\d{1,2}))?'  # Дата перегляду (день.місяць), якщо є
                r'(?:\s+(\d{1,2}(?:\.\d+)?/10))?'  # Рейтинг (число/10), якщо є
                r'(?:\s+([+\-]+))?$',          # Умови перегляду (++, +++, +-+), якщо є
                line)
            
            if match:
                print(f"Match: {match.groups()}")
            else:
                print(f"No match for line: {line}")

            if not match:
                bot.send_message(chat_id, f'Помилка обробки рядка: {line}')
                continue
            title = match.group(1).strip()
            date = match.group(2)
            rating = match.group(3)
            conditions = match.group(4)
            if date:
                day, month = date.strip().split('.')
                date = f"{year_int}-{int(month):02d}-{int(day):02d}" if year_int else None
            else:
                date = year_int
            if rating: #TODO: Check does it work
                rating = float(rating.split('/')[0])
                if 0 <= rating <= 10:
                    rating = round(rating, 1)
            else:
                rating = None

            if conditions == '+':
                condition = 'Сам вдома'
            elif conditions == '++':
                condition = 'З кимось вдома'
            elif conditions == '+++':
                condition = 'На великих екранах'
            elif conditions == '+-+':
                condition = 'З кимось, а потім сам'
            elif conditions == '-':
                condition = 'Недодивився'
            else:
                condition = None

            db.films.insert_one({
                'title': title,
                'rating': rating,
                'date': date,
                'conditions': condition,
                'year': year_int
            })
        except Exception as e:
            bot.send_message(chat_id, f'Помилка обробки рядка: {e} в {line}')
            continue

    bot.send_message(chat_id, 'Фільми успішно додано!')