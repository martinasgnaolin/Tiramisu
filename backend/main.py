import asyncio
import sys
import logging
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.sql.expression import func

import db
import github_apikey

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

STATUS_OK = 'success'
STATUS_ALREADY_LOGGED_IN = 'already_logged_in'
STATUS_AUTH_FAILED = 'authentication_failed'


def send_notification(chat_id: str, message: str):
    requests.post(
        'http://frontend:5000/notification',
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        json = {
            'chat_id': chat_id,
            'message': message
        }
    )

def get_authenticated_user(tg_chat_id):
    with db.session() as session:
        user = session.query(db.User).filter_by(telegram_id = tg_chat_id).first()
        if user is None or user.github_access_token is None:
            return None
        return user


def github_auth_begin():
    res = requests.post(
        'https://github.com/login/device/code',
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        json = {
            'client_id': github_apikey.CLIENT_ID,
            'scope': 'repo'
        }
    ).json()

    for field in ['device_code', 'user_code', 'verification_uri', 'expires_in', 'interval']:
        assert field in res

    return res

async def github_auth_loop(device_code, interval):
    while True:
        res = requests.post(
            'https://github.com/login/oauth/access_token',
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            json = {
                'client_id': github_apikey.CLIENT_ID,
                'device_code': device_code,
                'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
            }
        ).json()

        if 'error' in res:

            if res['error'] == 'slow_down':
                interval = res['interval']
                logging.info(f'GH auth, slowing down, interval {interval}')
            elif res['error'] == 'authorization_pending':
                logging.info(f'GH auth, pending')
            else:
                logging.warn(f'GH auth, error: {res}')

        elif 'access_token' in res:
            return res['access_token']

        await asyncio.sleep(interval)

async def github_auth_get_token(tg_chat_id, request):
    device_code = request['device_code']
    expires_in = request['expires_in']
    interval = request['interval']

    try:
        access_token = await asyncio.wait_for(
            github_auth_loop(device_code, interval),
            timeout = expires_in
        )
    except asyncio.TimeoutError:
        logging.info(f'GH auth, timed out')
        send_notification(tg_chat_id, 'Login timed out. Please try again.')
        return
    except Exception as e:
        logging.warn(f'GH auth, got exception {e}')
        send_notification(tg_chat_id, 'Login failed. Please try again.')
        return

    with db.session() as session:
        user = session.query(db.User).filter_by(telegram_id = tg_chat_id).first()

        if user:
            user.github_access_token = access_token
        else:
            user = db.User(
                telegram_id = tg_chat_id,
                github_access_token = access_token,
                notifications_enabled = True
            )
            session.add(user)

        session.commit()

    logging.info(f'GH auth success, chat id {tg_chat_id}, access token {access_token}')
    send_notification(tg_chat_id, 'Logged in successfully.')

app = FastAPI()

@app.on_event('startup')
def app_startup():
    db.init()


class ApiRequest(BaseModel):
    tg_chat_id: str

class ConnectRequest(ApiRequest): pass

class RemoveRequest(ApiRequest): pass

class SubscriptionAddRequest(ApiRequest):
    owner: str
    repo: str
    pattern: str

class SubscriptionListRequest(ApiRequest): pass

class SubscriptionDeleteRequest(ApiRequest):
    sub_id: str


@app.post('/user/connect')
async def api_user_connect(req: ConnectRequest):
    if get_authenticated_user(req.tg_chat_id):
        return {'status': STATUS_ALREADY_LOGGED_IN}

    gh_request = github_auth_begin()
    asyncio.create_task(github_auth_get_token(req.tg_chat_id, gh_request))

    return {
        'status': STATUS_OK,
        'verification_uri': gh_request['verification_uri'],
        'user_code': gh_request['user_code']
    }

@app.post('/user/remove')
def api_user_remove(req: RemoveRequest):
    if not (user := get_authenticated_user(req.tg_chat_id)):
        return {'status': STATUS_AUTH_FAILED}

    with db.session() as session:
        session.query(db.User).filter_by(id = user.id).first().github_access_token = None
        session.commit()

    return {'status': STATUS_OK}


@app.get('/notifications/enable')
def api_notifications_enable():
    return {'no':'no'}

@app.get('/notifications/disable')
def api_notifications_enable():
    return {'no':'no'}


@app.post('/subscription')
def api_subscription(req: SubscriptionAddRequest):
    if not (user := get_authenticated_user(req.tg_chat_id)):
        return {'status': STATUS_AUTH_FAILED}

    with db.session() as session:
        last_sub_id = session.query(func.max(db.Subscription.id)).filter_by(user_id = user.id).first()
        if not last_sub_id:
            last_sub_id = 0

        sub = db.Subscription(
            id = last_sub_id + 1,
            user_id = user.id,
            owner = req.owner,
            repo = req.repo,
            pattern = req.pattern
        )

        session.add(sub)
        session.commit()

    return {'status': STATUS_OK}

@app.post('/subscription/list')
def api_subscription_list(req: SubscriptionListRequest):
    if not (user := get_authenticated_user(req.tg_chat_id)):
        return {'status': STATUS_AUTH_FAILED}

    with db.session() as session:
        subs = session.query(db.Subscription).filter_by(user_id = user.id).order_by(db.Subscription.id).all()

    res = []
    for sub in subs:
        res.append({
            'id': sub.id,
            'owner': sub.owner,
            'repo': sub.repo,
            'pattern': sub.pattern
        })

    return {
        'status': STATUS_OK,
        'result': res
    }

@app.post('/subscription/delete')
def api_subscription_delete(req: SubscriptionDeleteRequest):
    if not (user := get_authenticated_user(req.tg_chat_id)):
        return {'status': STATUS_AUTH_FAILED}

    with db.session() as session:
        sub = session.query(db.Subscription).filter_by(user_id = user.id, id = req.sub_id).first()
        if sub:
            sub.delete()

        session.commit()

    return {'status': STATUS_OK}


@app.post('/github_callback')
def github_callback():
    return {'no':'no'}
