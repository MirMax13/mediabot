from telebot import types
from variables.globals import media_type

def safe_quick_markup(buttons: dict) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    if not isinstance(buttons, dict):
        return markup
    
    valid_buttons = []
    for text, cfg in buttons.items():
        if not cfg or not isinstance(cfg, dict):
            continue
        cb = cfg.get('callback_data')
        url = cfg.get('url')
        if cb:
            valid_buttons.append(types.InlineKeyboardButton(text=text, callback_data=cb))
        elif url:
            valid_buttons.append(types.InlineKeyboardButton(text=text, url=url))
    
    for i in range(0, len(valid_buttons), 2):
        if i + 1 < len(valid_buttons):
            markup.row(valid_buttons[i], valid_buttons[i+1])
        else:
            markup.row(valid_buttons[i])
    
    return markup

def markup_buttons(chat_id, media_id, media_data):
    if chat_id != media_data['user_id']:
        buttons = {
            'Назад': {'callback_data': f'back_to_list_{media_type[chat_id]}'}
        }
    else:
        buttons = {
            'Назад': {'callback_data': f'back_to_list_{media_type[chat_id]}'},
            'Редагувати': {'callback_data': f'edit_{media_type[chat_id]}_{media_id}'},
            'Видалити': {'callback_data': f'delete_{media_type[chat_id]}_{media_id}'},
            'Перенести до переглянутого': {'callback_data': f'mark_as_watched_{media_type[chat_id]}_{media_id}'} if media_data.get('status') == 'waiting' else None
        }
    # Фільтруємо None значення
    buttons = {k: v for k, v in buttons.items() if v is not None}
    return safe_quick_markup(buttons)