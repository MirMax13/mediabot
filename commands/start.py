from config import bot

# TODO: fix using command while adding/editing
def send_welcome(message):
        command_list = """
        Привіт, ось список команд:

        Допоміжні команди:
        /start - допомога з командами

        Команди для додавання:
        /add_movie - додати фільм
        /add_game - додати гру
        /add_book - додати книгу
        /add_many_movies - додати багато фільмів (лише адмін)
        /add_many_games - додати багато ігор (лише адмін)

        Команди для пошуку:
        /search_movie - пошук фільму
        /search_game - пошук гри
        /search_book - пошук книги
        
        Команди для перегляду:
        /list - список контенту,ігор, книг
        /list_admin - список контенту,ігор, книг адміна

        Команди для адміністрування:
        /admin - адмін панель
"""
        bot.reply_to(message, command_list)