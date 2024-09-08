import re
from config import bot
from db import db
from datetime import datetime
from functions.admin_check import is_user_admin

def add_many_games(message):
    chat_id = message.chat.id
    if not is_user_admin(message):
        bot.send_message(chat_id, "Ви не адміністратор")
        return
    bot.send_message(chat_id, 'Введи текстом увесь вміст файлу')
    bot.register_next_step_handler(message, process_many_games)

def process_many_games(message):
    chat_id = message.chat.id
    text = message.text
    lines = text.split('\n')
    
    # Мапа українських місяців на англійські
    uk_to_en_months = {
        'січня': 'January', 'лютого': 'February', 'березня': 'March', 'квітня': 'April',
        'травня': 'May', 'червня': 'June', 'липня': 'July', 'серпня': 'August',
        'вересня': 'September', 'жовтня': 'October', 'листопада': 'November', 'грудня': 'December'
    }

    for line in lines:
        if not line.strip():
            continue
        try:
            match = re.match(
                r'^(.+?)'                           # Назва гри
                r'(?:\s+(\d{1,2}(?:\.\d+)?/10))?'   # Рейтинг (число/10), якщо є
                r'(?:\s+([+\-! ]+))?'                 # Умови, якщо є
                r'(?:\s+(\d{1,2}\s[а-яіїєґ]+\s\d{4}|[а-яіїєґ]+\s\d{4}))?$',  # Дата (день місяць рік або місяць рік), якщо є
                line)
            
            if match:
                print(f"Match: {match.groups()}")
            else:
                print(f"No match for line: {line}")

            if not match:
                bot.send_message(chat_id, f'Помилка обробки рядка: {line}')
                continue

            title = match.group(1).strip()
            rating = match.group(2)
            conditions = match.group(3)
            date_str = match.group(4)

            if date_str: #TODO: Fix partical date parsing
                try:
                    # Замінюємо український місяць на англійський
                    for uk_month, en_month in uk_to_en_months.items():
                        date_str = date_str.replace(uk_month, en_month)
                    # Парсинг дати з англійським місяцем
                    if re.match(r'\d{1,2}\s\w+\s\d{4}', date_str):
                        date = datetime.strptime(date_str, "%d %B %Y")
                        date = date.strftime("%Y-%m-%d")
                    else:
                        date = datetime.strptime(date_str, "%B %Y")
                        date = date.strftime("%Y-%m")
                    year = date.split('-')[0]
                    if int(year) < 2000 or int(year) > datetime.now().year:
                        bot.send_message(chat_id, f'Помилка у році дати: {date_str} в {line}')
                        continue
                except ValueError:
                    bot.send_message(chat_id, f'Помилка у форматі дати: {date_str} в {line}')
                    continue
                
            else:
                date = None
                year = None

            if rating:
                rating = float(rating.split('/')[0])
                if 0 <= rating <= 10:
                    rating = round(rating, 1)
            else:
                rating = None

            condition_map = {
                '+': 'Подивився',
                '+-': 'Дивився',
                '++': 'Пройшов',
                '++-': 'Грав',
                '+ ++-': 'Подивився повністю, а потім зіграв',
                '+ ++': 'Подивився повністю, а потім пройшов повністю',
                '+- ++-': 'Дивився, а потім зіграв',
                '!+': 'Слухав сюжет',
                '+- !+ ++-': 'Дивився, а потім слухав сюжет, а потім зіграв',
                '+- !+': 'Дивився, а потім слухав сюжет',
                '!++': 'Грав (неможливо пройти)',
                '+- !++': 'Дивився, а потім грав (неможливо пройти)',
                '+++': 'Пройшов разом з DLC',
                '+- +++': 'Дивився, а потім пройшов разом з DLC',
            }

            condition = condition_map.get(conditions.strip()) if conditions else None

            db.games.insert_one({
                'title': title,
                'rating': rating,
                'date': date,
                'year': year,
                'conditions': condition,
            })
        except Exception as e:
            bot.send_message(chat_id, f'Помилка обробки рядка: {e} в {line}')
            continue

    bot.send_message(chat_id, 'Ігри успішно додано!')
