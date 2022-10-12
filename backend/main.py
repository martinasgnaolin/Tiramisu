import os
import sys
from fastapi import FastAPI
import psycopg
import logging
import time

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_CONNECTION_ATTEMPTS = 5
DB_CONNECTION_DELAY = 5

app = FastAPI()

@app.on_event('startup')
def app_startup():
    conn_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    for i in range(DB_CONNECTION_ATTEMPTS):
        try:
            app.state.db = psycopg.connect(conn_string)
            break
        except psycopg.OperationalError:
            logging.info(f'Database connection failed ({i+1}/{DB_CONNECTION_ATTEMPTS}).')
            if i < DB_CONNECTION_ATTEMPTS - 1:
                logging.info(f'Retrying in {DB_CONNECTION_DELAY}s.')
                time.sleep(DB_CONNECTION_DELAY)
    else:
        raise RuntimeError(f'Database connection failed for {DB_CONNECTION_ATTEMPTS} attempts. Shutting down')

    logging.info(f'Database connected {app.state.db}')

@app.on_event('shutdown')
def app_shutdown():
    app.state.db.close()
    logging.info(f'Database connection shut down')


@app.post('/user/connect')
def api_user_connect():
    return {'no':'no'}

@app.get('/notifications/enable')
def api_notifications_enable():
    return {'no':'no'}

@app.get('/notifications/disable')
def api_notifications_enable():
    return {'no':'no'}

@app.post('/subscription/add')
def api_subscription():
    return {'no':'no'}

@app.get('/subscription/list')
def api_subscription_list():
    return {'no':'no'}

@app.delete('/subscription/{id}')
def api_subscription_id(id: int):
    return {'no':'no'}


@app.post('/github_callback')
def github_callback():
    return {'no':'no'}
