from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()
MONGODB_PASSWORD=os.environ.get('MONGODB_PASSWORD')
NICKNAME=os.environ.get('NICKNAME')
uri = f'mongodb+srv://{NICKNAME}:{MONGODB_PASSWORD}@mediabot.ksszufh.mongodb.net/?retryWrites=true&w=majority&appName=MediaBot'
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['mediadatabase']

films = db['films']
books = db['books']
games = db['games']
