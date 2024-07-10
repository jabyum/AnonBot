from database import get_db
from database.models import User, Channels, Messages, Link_statistic, Answer_statistic, Rating_overall, Rating_today
from datetime import datetime
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import Session
import pytz
moscow_timezone = pytz.timezone('Europe/Moscow')


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
        new_user = User(tg_id=tg_id, user_link=link, reg_date=datetime.now(moscow_timezone))
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
                                receiver_message_id=receiver_message_id,
                                reg_date=datetime.now(moscow_timezone).strftime("%Y-%m-%d"))
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


def add_rating_today(tg_id):
    with (next(get_db()) as db):
        actual_date = datetime.now(moscow_timezone).strftime("%Y-%m-%d")
        user = db.query(Rating_today).filter_by(user_id=tg_id).filter(Rating_today.reg_date == actual_date).first()
        if not user:
            new_user = Rating_today(user_id=tg_id, amount=1, reg_date=datetime.now(moscow_timezone).strftime("%Y-%m-%d"))
            db.add(new_user)
            db.commit()
        elif user:
            user.amount += 1
            db.commit()
        else:
            new_user = Rating_today(user_id=tg_id, amount=1, reg_date=datetime.now(moscow_timezone).strftime("%Y-%m-%d"))
            db.add(new_user)
            db.commit()


def add_rating_overall(tg_id):
    with next(get_db()) as db:
        user = db.query(Rating_overall).filter_by(user_id=tg_id).first()
        if not user:
            new_user = Rating_overall(user_id=tg_id, amount=1, reg_date=datetime.now(moscow_timezone).strftime("%Y-%m-%d"))
            db.add(new_user)
            db.commit()
        elif user:
            user.amount += 1
            db.commit()
        else:
            new_user = Rating_today(user_id=tg_id, amount=1, reg_date=datetime.now(moscow_timezone).strftime("%Y-%m-%d"))
            db.add(new_user)
            db.commit()
def add_link_statistic(tg_id):
    with next(get_db()) as db:
        new_user = Link_statistic(user_id=tg_id, reg_date=datetime.now(moscow_timezone).strftime("%Y-%m-%d"))
        db.add(new_user)
        db.commit()
        add_rating_today(tg_id)
        add_rating_overall(tg_id)
def add_answer_statistic(tg_id):
    with next(get_db()) as db:
        new_user = Answer_statistic(user_id=tg_id, reg_date=datetime.now(moscow_timezone).strftime("%Y-%m-%d"))
        db.add(new_user)
        db.commit()
def value_handler(num):
    if not num:
        return 0
    return num
def get_all_statistic(tg_id: int):
    #TODO подклюние к бд учесть в конструкторе
    engine = create_engine('sqlite:///anonchatbot.db', echo=False, connect_args={'check_same_thread': False})
    db = Session(bind=engine)
    actual_date = datetime.now(moscow_timezone).strftime("%Y-%m-%d")
    messages_today = (db.query(Messages).filter(Messages.receiver_id == tg_id).
                      filter(Messages.reg_date == actual_date).count())
    messages_overall = db.query(Messages).filter_by(receiver_id=tg_id).count()
    answers_today = (db.query(Answer_statistic).filter(Answer_statistic.user_id == tg_id).
                     filter(Answer_statistic.reg_date == actual_date).count())
    answers_overall = db.query(Rating_overall).filter_by(user_id=tg_id).count()
    links_today = (db.query(Link_statistic).filter(Link_statistic.user_id == tg_id).
                   filter(Link_statistic.reg_date == actual_date).count())
    links_overall = db.query(Link_statistic).filter_by(user_id=tg_id).count()
    rating_today = (db.query(Rating_today).filter(Rating_today.reg_date == actual_date).
                    order_by(desc(Rating_today.amount)).all())
    rating_overall = db.query(Rating_overall).order_by(desc(Rating_overall.amount)).all()

    position_today = 1
    for rating in rating_today:
        if rating.user_id == tg_id:
            break
        elif position_today == 1000:
            position_today = "1000+"
        else:
            position_today += 1
    position_overall = 1
    for rating in rating_overall:
        if rating.user_id == tg_id:
            break
        elif position_overall == 1000:
            position_overall = "1000+"
        else:
            position_overall += 1
    db.close()
    return {"messages_today": value_handler(messages_today),
            "answers_today": value_handler(answers_today),
            "links_today": value_handler(links_today),
            "position_today": position_today,
            "messages_overall": messages_overall,
            "answers_overall": answers_overall,
            "links_overall": links_overall,
            "position_overall": position_overall}






