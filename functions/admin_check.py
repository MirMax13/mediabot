import os

ADMIN_ID = os.environ.get('ADMIN_ID')

def is_user_admin(message):
    user_id = message.from_user.id
    if str(user_id) in ADMIN_ID:
        return True
    else:
        return False