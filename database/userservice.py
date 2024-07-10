from database import get_db
from database.models import User, Channels, Messages, Link_statistic
from datetime import datetime

def get_channels_for_check():
    with next(get_db()) as db:
        all_channels = db.query(Channels).all()
        if all_channels:
            return [[i.channel_id, i.channel_url] for i in all_channels]
        return []
def check_user(tg_id):
    with next(get_db()) as db:
        checker = db.query(User).filter_by(tg_id=tg_id).first()
        if checker:
            return True
        return False
def add_user(tg_id, link):
    with next(get_db()) as db:
        new_user = User(tg_id=tg_id, user_link=link, reg_date=datetime.now())
        db.add(new_user)
        db.commit()

def get_user_by_link(link):
    with next(get_db()) as db:
        check_user = db.query(User).filter_by(user_link=link).first()
        if check_user:
            return check_user.tg_id
        return False
def add_messages_info(sender_id, receiver_id, sender_message_id, receiver_message_id):
    with next(get_db()) as db:
        new_messages = Messages(sender_id=sender_id, receiver_id=receiver_id, sender_message_id=sender_message_id,
                                receiver_message_id=receiver_message_id, reg_date=datetime.now())
        db.add(new_messages)
        db.commit()
def get_user_link(tg_id):
    with next(get_db()) as db:
        check_user = db.query(User).filter_by(tg_id=tg_id).first()
        if check_user:
            return check_user.user_link
        return False

def check_reply(receiver_message_id):
    with next(get_db()) as db:
        check_user = db.query(Messages).filter_by(receiver_message_id=receiver_message_id).first()
        if check_user:
            return [check_user.sender_id, check_user.sender_message_id]
        return False
def change_greeting_user(tg_id, greeting=None):
    with next(get_db()) as db:
        user = db.query(User).filter_by(tg_id=tg_id).first()
        if user:
            user.greeting = greeting
            db.commit()
def get_greeting(tg_id):
    with next(get_db()) as db:
        user = db.query(User).filter_by(tg_id=tg_id).first()
        if user:
            return user.greeting
        return False
def check_link(link):
    with next(get_db()) as db:
        user = db.query(User).filter_by(user_link=link).first()
        if user:
            return False
        return True
def change_link_db(tg_id, new_link):
    with next(get_db()) as db:
        user = db.query(User).filter_by(tg_id=tg_id).first()
        if user:
            user.user_link = new_link
            db.commit()