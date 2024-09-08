from config import bot
from functions.admin_check import is_user_admin

def admin_panel(message):
    status = is_user_admin(message)
    if status:
        bot.send_message(message.chat.id, "Ви адміністратор")
    else:
        bot.send_message(message.chat.id, "Ви не адміністратор")


