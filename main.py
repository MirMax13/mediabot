import os
from flask import Flask, request
import telebot
from config import bot
import bot as bot_handlers
app = Flask(__name__)

@app.route('/', methods=['GET'])
def alive():
    return 'Bot is alive!', 200

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data(as_text=True)
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Invalid request', 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)