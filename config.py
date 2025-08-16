from dotenv import load_dotenv
import os
from telebot import TeleBot
from collections import defaultdict

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_MODE = os.environ.get('BOT_MODE', 'polling')  # default polling
bot = TeleBot(BOT_TOKEN)

params_dict = defaultdict(dict)