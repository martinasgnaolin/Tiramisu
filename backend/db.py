import logging
import time
import os

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, Session
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

    def __repr__(self):
        return f'User(id={self.id}, telegram_id={self.telegram_id}, notifications_enabled={self.notifications_enabled})'


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
