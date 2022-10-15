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

# Just to test if connection is working, to be removed
@app.get('/test')
def api_test():
    return {"message": "Hello World"}

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
    update.message.reply_text("Login with your GitHub account (TODO)")

def logout_command(update, context):
    update.message.reply_text("Logout from your GitHub account (TODO)")

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

def subscribe_command(update, context):
    update.message.reply_text("Which subscription do you want to add?")

def unsubscribe_command(update, context):
    update.message.reply_text("Which subscription do you want to remove?")

def subscriptions_command(update, context):
    response = requests.get('http://backend:8000/subscription/list')
    # Here we'll iterate over the list in the response and return all elements

#----------------------------------
# Main
#----------------------------------

def error(update, context):
    print(f"Update {update} caused error {context.error}")

def main():
    updater = Updater(API_KEY, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("login", login_command))
    dp.add_handler(CommandHandler("logout", logout_command))
    dp.add_handler(CommandHandler("enable", enable_command))
    dp.add_handler(CommandHandler("disable", disable_command))
    dp.add_handler(CommandHandler("subscribe", subscribe_command))
    dp.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    dp.add_handler(CommandHandler("subscriptions", subscriptions_command))

    updater.start_polling(1)
    updater.idle()

main()