from config import bot

@bot.message_handler(commands=['start', 'hello']) # TODO: fix using command while adding/editing
def send_welcome(message):
        bot.reply_to(message, "Howdy, how are you doing?")