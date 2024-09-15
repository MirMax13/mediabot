from config import bot
from commands.add_movie import add_movie
from commands.add_game import add_game
from commands.add_book import add_book
from commands.list_items import list_user_items, list_admin_items
from commands.add_many_movies import add_many_movies
from commands.add_many_games import add_many_games
from commands.start import send_welcome
from commands.search_movie import search_movie
from commands.search_game import search_game
from commands.search_book import search_book
from commands.admin import admin_panel

bot.message_handler(commands=['add_movie'])(add_movie)
bot.message_handler(commands=['add_game'])(add_game)
bot.message_handler(commands=['add_book'])(add_book)
bot.message_handler(commands=['list'])(list_user_items)
bot.message_handler(commands=['list_admin'])(list_admin_items)
bot.message_handler(commands=['add_many_movies'])(add_many_movies)
bot.message_handler(commands=['add_many_games'])(add_many_games)
bot.message_handler(commands=['start'])(send_welcome)
bot.message_handler(commands=['search_movie'])(search_movie)
bot.message_handler(commands=['search_game'])(search_game)
bot.message_handler(commands=['search_book'])(search_book)
bot.message_handler(commands=['admin'])(admin_panel)


bot.delete_webhook()
bot.infinity_polling()