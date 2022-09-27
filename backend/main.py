import os
from fastapi import FastAPI
import psycopg
import logging

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

app = FastAPI()

@app.on_event('startup')
def app_startup():
    logging.getLogger().setLevel(logging.INFO)

    conn_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    app.state.db = psycopg.connect(conn_string)
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
