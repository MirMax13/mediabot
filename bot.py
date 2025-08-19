from config import bot
from commands.titles.adding.add_movie import add_movie
from commands.titles.adding.add_series import add_series
from commands.titles.adding.add_anime import add_anime_series, add_anime_movie
from commands.titles.adding.add_animated import add_animated_movie, add_animated_series
from commands.games.add_game import add_game
from commands.books.add_book import add_book
from commands.list_items import list_user_items, list_admin_items, list_waiting_items
from commands.titles.adding.add_many_movies import add_many_movies
from commands.games.add_many_games import add_many_games
from commands.titles.adding.add_waiting import add_waiting_media
from commands.start import send_welcome
from commands.titles.searching.search_movie import search_user_movie, search_admin_movie
from commands.games.search_game import search_user_game, search_admin_game
from commands.books.search_book import search_user_book, search_admin_book
from commands.admin import admin_panel
from commands.change_language import change_language

bot.message_handler(commands=['add_movie'])(add_movie)
bot.message_handler(commands=['add_serias'])(add_series)
bot.message_handler(commands=['add_anime_series'])(add_anime_series)
bot.message_handler(commands=['add_anime_movie'])(add_anime_movie)
bot.message_handler(commands=['add_animated_movie'])(add_animated_movie)
bot.message_handler(commands=['add_animated_series'])(add_animated_series)
bot.message_handler(commands=['add_waiting'])(add_waiting_media)
bot.message_handler(commands=['add_game'])(add_game)
bot.message_handler(commands=['add_book'])(add_book)
bot.message_handler(commands=['list'])(list_user_items)
bot.message_handler(commands=['list_admin'])(list_admin_items)
bot.message_handler(commands=['list_waiting'])(list_waiting_items)
bot.message_handler(commands=['add_many_movies'])(add_many_movies)
bot.message_handler(commands=['add_many_games'])(add_many_games)
bot.message_handler(commands=['start'])(send_welcome)
bot.message_handler(commands=['search_movie'])(search_user_movie)
bot.message_handler(commands=['search_game'])(search_user_game)
bot.message_handler(commands=['search_book'])(search_user_book)
bot.message_handler(commands=['search_movie_admin'])(search_admin_movie)
bot.message_handler(commands=['search_game_admin'])(search_admin_game)
bot.message_handler(commands=['search_book_admin'])(search_admin_book)
bot.message_handler(commands=['admin'])(admin_panel)
bot.message_handler(commands=['change_language'])(change_language)


# bot.delete_webhook()
# bot.infinity_polling()
from config import BOT_MODE
if __name__ == "__main__":
    if BOT_MODE == "polling":
        print("🚀 Запускаю бота в режимі POLLING (локальна розробка)")
        bot.delete_webhook()
        bot.infinity_polling()
    else:
        print("🌐 BOT_MODE != polling — не запускаємо локально")