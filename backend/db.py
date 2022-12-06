import logging
import time
import os

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, Session, relationship
from sqlalchemy.exc import OperationalError

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_CONNECTION_ATTEMPTS = 5
DB_CONNECTION_DELAY = 5

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(String, nullable=False, unique=True)
    github_access_token = Column(String)
    notifications_enabled = Column(Boolean, nullable=False, default=True)

    subscriptions = relationship("Subscription", cascade="all, delete")

    def __repr__(self):
        return f'User(id={self.id}, telegram_id={self.telegram_id}, notifications_enabled={self.notifications_enabled})'


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

    owner = Column(String, nullable=False)
    repo = Column(String, nullable=False)
    pattern = Column(String, nullable=False)

    def __repr__(self):
        return f'Subscription(id={self.id}, user_id={self.user_id}, owner={self.owner}, repo={self.repo}, pattern={self.pattern})'


def init():
    conn_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    for i in range(DB_CONNECTION_ATTEMPTS):
        try:
            engine = create_engine(conn_string)
            engine.connect()
            break
        except OperationalError:
            logging.info(f'Database connection failed ({i+1}/{DB_CONNECTION_ATTEMPTS}).')
            if i < DB_CONNECTION_ATTEMPTS - 1:
                logging.info(f'Retrying in {DB_CONNECTION_DELAY}s.')
                time.sleep(DB_CONNECTION_DELAY)
    else:
        raise RuntimeError(f'Database connection failed for {DB_CONNECTION_ATTEMPTS} attempts. Shutting down')

    Base.metadata.bind = engine
    Base.metadata.create_all()

    logging.info('Database initialized')

def session():
    return Session(Base.metadata.bind)
