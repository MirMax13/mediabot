from config import bot

# TODO: fix using command while adding/editing
def send_welcome(message):
        command_list = """
        Привіт, ось список команд:

        Допоміжні команди:
        /start - допомога з командами

        Команди для додавання:
        /add_movie - додати фільм
        /add_serias = додати серіал
        /add_anime_movie - додати аніме фільм
        /add_anime_series - додати аніме серіал
        /add_animated_movie - додати мультфільм
        /add_animated_series - додати мультсеріал
        /add_game - додати гру
        /add_book - додати книгу
        /add_many_movies - додати багато фільмів (лише адмін)
        /add_many_games - додати багато ігор (лише адмін)

        Команди для пошуку:
        /search_movie - пошук фільму
        /search_game - пошук гри
        /search_book - пошук книги
        /search_movie_admin - пошук фільму адміна
        /search_game_admin - пошук гри адміна
        /search_book_admin - пошук книги адміна
        
        Команди для перегляду:
        /list - список контенту,ігор, книг
        /list_admin - список контенту,ігор, книг адміна

        Команди для адміністрування:
        /admin - адмін панель
"""
        bot.reply_to(message, command_list)