from telegram.ext import *

from telegram_apikey import API_KEY

import requests
from fastapi import FastAPI
from pydantic import BaseModel

print("Bot started...")

#----------------------------------
# Fast API
#----------------------------------

class Notification(BaseModel):
    message: str
    chat_id: str

app = FastAPI()

@app.post('/notification')
async def api_notification(notification: Notification):
    updater = Updater(API_KEY)
    updater.bot.sendMessage(chat_id=notification.chat_id, text=notification.message)


#---------------------------------
# Start and Help commands
#---------------------------------

def start_command(update, context):
    update.message.reply_text(
        "Hello. I will help you manage your GitHub notifications. If you need it, use the command /help \n"
        "These are the commands you can use:\n"
        "- To login to your GitHub account: /login \n"
        "- To log off your GitHub account: /logout \n"
        "- To start receiving notifications: /enable \n"
        "- To disable the service: /disable \n"
        "- To add a new subscription: /subscribe \n"
        "- To delete some subscription: /unsubscribe \n"
        "- To get a list of your current subscriptions: /subscriptions \n"
    )

def help_command(update, context):
    update.message.reply_text(
        "These are the commands you can use:\n"
        "- To login to your GitHub account: /login \n"
        "- To log off your GitHub account: /logout \n"
        "- To start receiving notifications: /enable \n"
        "- To disable the service: /disable \n"
        "- To add a new subscription: /subscribe \n"
        "- To delete some subscription: /unsubscribe \n"
        "- To get a list of your current subscriptions: /subscriptions \n"
    )


#---------------------------------
# Login and logout
#---------------------------------

def login_command(update, context):

    res = requests.post(
        'http://backend:8000/user/connect',
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        json = {
            'tg_chat_id': update.message.chat.id
        }
    ).json()

    if res['status'] == 'success':
        uri = res['verification_uri']
        code = "`" + res['user_code'] + "`"
        update.message.reply_text("Follow the link " + uri 
                                  + " and insert the following code (tap to copy): "
                                  + code, parse_mode="Markdown")
    
    if res['status'] == 'already_logged_in':
        update.message.reply_text("You are already logged in")

def logout_command(update, context):
    
    res = requests.post(
        'http://backend:8000/user/remove',
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        json = {
            'tg_chat_id': update.message.chat.id
        }
    ).json()

    if res['status'] == 'success':
        update.message.reply_text("Successfully logged out")
    
    if res['status'] == 'authentication_failed':
        update.message.reply_text("Log out failed: you are not logged in")


#----------------------------------
# Notifications enabling/disabling
#----------------------------------

def enable_command(update, context):
    response = requests.get('http://backend:8000/notifications/enable')
    if response.status_code == 200:
        update.message.reply_text("Now the service is enabled")
    else:
        update.message.reply_text("Some error occurred, please try again")

def disable_command(update, context):
    response = requests.get('http://backend:8000/notifications/disable')
    if response.status_code == 200:
        update.message.reply_text("Now the service is disabled")
    else:
        update.message.reply_text("Some error occurred, please try again")


#----------------------------------
# Subscriptions handling
#----------------------------------

OWNER, REPO, PATTERN, COMPLETE = range(4)

def subscribe_command(update, context):
    update.message.reply_text("Let's add a new subscription. Which is the owner?")
    return OWNER

def get_owner(update, context):
    context.user_data['owner'] = update.message.text
    update.message.reply_text("Which is the repo?")
    return REPO

def get_repo(update, context):
    context.user_data['repo'] = update.message.text
    update.message.reply_text("Which is the pattern?")
    return PATTERN

def get_pattern(update, context):
    context.user_data['pattern'] = update.message.text

    response = requests.post(
        'http://backend:8000/subscription',
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        json = {
            'tg_chat_id': update.message.chat.id,
            'owner': context.user_data['owner'],
            'repo': context.user_data['repo'],
            'pattern': context.user_data['pattern']
        }
    ).json()

    if response['status'] == 'success':
        update.message.reply_text("Subscription successfully added")    
    if response['status'] == 'authentication_failed':
        update.message.reply_text("Authentication failed")
    
    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text("Conversation concluded")
    return ConversationHandler.END
       
def unsubscribe_command(update, context):
    update.message.reply_text("Which subscription do you want to remove?")

def subscriptions_command(update, context):
    response = requests.get('http://backend:8000/subscription/list')
    if response['status'] == 'success':
        string = "These are your current subscriptions:\n"
        for s in response['result']:
            string += s['id']+':'+s['owner']+':'+s['repo']+':'+s['pattern']
            string += "\n"
        update.message.reply_text(string)
    if response['status'] == 'authentication_failed':
        update.message.reply_text('Authentication failed')


#----------------------------------
# Main
#----------------------------------

def error(update, context):
    print(f"Update {update} caused error {context.error}")

@app.on_event('startup')
def init_telegram_bot():
    updater = Updater(API_KEY, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("login", login_command))
    dp.add_handler(CommandHandler("logout", logout_command))
    dp.add_handler(CommandHandler("enable", enable_command))
    dp.add_handler(CommandHandler("disable", disable_command))
    #dp.add_handler(CommandHandler("subscribe", subscribe_command))
    #dp.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    dp.add_handler(CommandHandler("subscriptions", subscriptions_command))

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("subscribe", subscribe_command)],
        states={
            OWNER: [MessageHandler(Filters.text, get_owner)],
            REPO: [MessageHandler(Filters.text, get_repo)],
            PATTERN: [MessageHandler(Filters.text, get_pattern)]

        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )    
    dp.add_handler(conversation_handler)

    updater.start_polling(1)