import asyncio
import sys
import logging
import requests
from fastapi import FastAPI

import db
import github_apikey

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


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

async def github_auth_get_token(request):
    device_code = request['device_code']
    expires_in = request['expires_in']
    interval = request['interval']

    try:
        access_token = await asyncio.wait_for(
            github_auth_loop(device_code, interval),
            timeout = expires_in
        )
    except TimeoutError:
        logging.info(f'Github authorization timed out')

    logging.info(f'GH auth success, access token {access_token}')


app = FastAPI()

@app.on_event('startup')
def app_startup():
    db.init()


@app.post('/user/connect')
async def api_user_connect():
    request = github_auth_begin()
    asyncio.create_task(github_auth_get_token(request))

    return {
        'verification_uri': request['verification_uri'],
        'user_code': request['user_code']
    }

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
