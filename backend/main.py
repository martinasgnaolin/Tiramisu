import os
import sys
from fastapi import FastAPI
import logging
import time
import db

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

app = FastAPI()

@app.on_event('startup')
def app_startup():
    db.init()


@app.post('/user/connect')
def api_user_connect():
    with db.session() as session:
        user = db.User(telegram_id='asd', notifications_enabled=False)
        session.add(user)
        session.commit()

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
