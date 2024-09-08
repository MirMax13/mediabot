from config import bot

# TODO: fix using command while adding/editing
def send_welcome(message):
        command_list = """
        Привіт, ось список команд:

        Допоміжні команди:
        /start - допомога з команлами

        Команди для додавання:
        /add_movie - додати фільм
        /add_game - додати гру
        /add_many_movies - додати багато фільмів (лише адмін)
        /add_many_games - додати багато ігор (лише адмін)

        Команди для пошуку:
        /search_movie - пошук фільму
        /search_game - пошук гри

        Команди для видалення:
        /delete_movie - видалити фільм
        /delete_game - видалити гру

        Команди для редагування:
        /edit_movie - редагувати фільм
        /edit_game - редагувати гру
        
        Команди для перегляду:
        /list - список фільмів та ігор

        Команди для адміністрування:
        /admin - адмін панель
"""
        bot.reply_to(message, command_list)