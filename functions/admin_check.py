import os

ADMIN_IDS = os.environ.get('ADMIN_IDS', '').split(',')

def is_user_admin(message):
    user_id = message.from_user.id
    if str(user_id) in ADMIN_IDS:
        return True
    else:
        return False