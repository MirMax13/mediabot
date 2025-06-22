import os
import threading
from flask import Flask
from config import bot
import bot as bot_handlers
app = Flask(__name__)

@app.route('/')
def alive():
    return 'Bot is alive!', 200

def run_bot():
    bot.delete_webhook()
    bot.infinity_polling()

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
