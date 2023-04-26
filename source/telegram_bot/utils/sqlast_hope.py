import sqlalchemy.orm
from .user import User
from .connect_creater import connect


generator = connect('telegram_bot/assets/secure/database.db')


def create_user(chat_id, message_id):
    usr = User()
    usr.chat_id = chat_id
    usr.message_id = message_id
    session = generator()
    session.add(usr)
    session.commit()


def user(chat_id) -> (User, sqlalchemy.orm.session.Session):
    session = generator()
    return session.query(User).get(chat_id), session


def delete_user(chat_id):
    usr, session = user(chat_id)
    usr.default()
    session.commit()
    session.close()
