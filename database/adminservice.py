from database import get_db
from database.models import *
def get_channels_for_admin():
    with next(get_db()) as db:
        all_channels = db.query(Channels).all()
        if all_channels:
            return [[i.id, i.channel_url, i.channel_id] for i in all_channels]
def add_new_channel_db(url, id):
    with next(get_db()) as db:
        new_channel = Channels(channel_url=url, channel_id=id)
        db.add(new_channel)
        db.commit()
        return True
def delete_channel_db(id):
    with next(get_db()) as db:
        channel = db.query(Channels).filter_by(id=id).first()
        if channel:
            db.delete(channel)
            db.commit()
            return True
        return False
def get_all_users_tg_id():
    with next(get_db()) as db:
        users = db.query(User).all()
        return [i.tg_id for i in users]

def get_users_count():
    with next(get_db()) as db:
        all_users = db.query(User).count()
        return all_users
