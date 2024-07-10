from sqlalchemy import (Column, Integer,
                        String, DateTime, Boolean)
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    tg_id = Column(Integer, unique=True)
    user_link = Column(String, unique=True)
    greeting = Column(String, nullable=True, default=None)
    reg_date = Column(DateTime)

class Messages(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer)
    receiver_id = Column(Integer)
    sender_message_id = Column(Integer)
    receiver_message_id = Column(Integer)
    reg_date = Column(String)

class Link_statistic(Base):
    __tablename__ = "link"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    reg_date = Column(String)

class Answer_statistic(Base):
    __tablename__ = "answer"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    reg_date = Column(String)

class Rating_today(Base):
    __tablename__ = "rating_today"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    amount = Column(Integer)
    reg_date = Column(String)
class Rating_overall(Base):
    __tablename__ = "rating_overall"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True)
    amount = Column(Integer)
    reg_date = Column(String)
class Channels(Base):
    __tablename__ = "channel"
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_url = Column(String, unique=True)
    channel_id = Column(Integer, unique=True)
    admins_channel = Column(Boolean, default=False)







