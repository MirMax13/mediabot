from telebot import types
from variables.globals import media_type
from telebot.util import quick_markup

def markup_buttons(chat_id, media_id, media_data):
    markup = types.InlineKeyboardMarkup()
    if chat_id != media_data['user_id']:
        markup = quick_markup({
            'Назад': {'callback_data': f'back_to_list_{media_type[chat_id]}'}
        })
    else:
        markup = quick_markup({
            'Назад': {'callback_data': f'back_to_list_{media_type[chat_id]}'},
            'Редагувати': {'callback_data': f'edit_{media_type[chat_id]}_{media_id}'},
            'Видалити': {'callback_data': f'delete_{media_type[chat_id]}_{media_id}'},
            'Перенести до переглянутого': {'callback_data': f'mark_as_watched_{media_type[chat_id]}_{media_id}'} if media_data.get('status') == 'waiting' else None
        })
    return markup