from config import bot
from commands.add_movie import add_movie
from commands.add_game import add_game
from commands.list_items import list_items
from commands.add_many_movies import add_many_movies
from commands.add_many_games import add_many_games
from commands.start import send_welcome
from commands.search_movie import search_movie


bot.message_handler(commands=['addmovie'])(add_movie)
bot.message_handler(commands=['addgame'])(add_game)
bot.message_handler(commands=['list'])(list_items)
bot.message_handler(commands=['addmanymovies'])(add_many_movies)
bot.message_handler(commands=['addmanygames'])(add_many_games)
bot.message_handler(commands=['start'])(send_welcome)
bot.message_handler(commands=['searchmovie'])(search_movie)


bot.delete_webhook()
bot.infinity_polling()