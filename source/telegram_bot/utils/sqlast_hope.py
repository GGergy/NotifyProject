import random
from .user import User
from threading import Thread
from time import sleep
from .connect_creater import connect


session = connect('telegram_bot/assets/secure/database.db')
delay = 3
ticks = 3


def try_commit():
    global session
    while True:
        try:
            session.commit()
        except Exception as e:
            print(f'commit failed: {e}')
            session = connect('telegram_bot/assets/secure/database.db')
        sleep(delay)


def create_user(chat_id):
    usr = User()
    usr.chat_id = chat_id
    for _ in range(ticks):
        try:
            session.add(usr)
        except Exception:
            sleep(random.random())


def user(chat_id) -> User:
    for _ in range(ticks):
        try:
            usr = session.query(User).get(chat_id)
            if not usr:
                create_user(chat_id)
            return session.query(User).get(chat_id)
        except Exception:
            sleep(random.random())


def delete_user(chat_id):
    usr = user(chat_id)
    usr.default()


commit_thread = Thread(target=try_commit)
commit_thread.start()
