from telegram.ext import *

API_KEY = '5745630007:AAGOStGrqivsJj-EO-lkt-M3ATf7QMmW450'

print("Bot started...")

def start_command(update, context):
    update.message.reply_text(
        "Hello. I will help you manage your GitHub notifications. If you need it, use the command /help \n"
        "These are the commands you can use:\n"
        "- To login to your GitHub account: /login \n"
        "- To log off your GitHub account: /logout \n"
        "- To start receiving notifications: /enable \n"
        "- To disable the service: /disable \n"
        "- Then we need to handle the subscriptions"
    )

def help_command(update, context):
    update.message.reply_text(
        "These are the commands you can use:\n"
        "- To login to your GitHub account: /login \n"
        "- To log off your GitHub account: /logout \n"
        "- To start receiving notifications: /enable \n"
        "- To disable the service: /disable \n"
        "- Then to handle the subscriptions:\n"
        "/subscribe - <repo> <file pattern[s]>; \n"
        "/subscriptions - list subscriptions \n"
        "/unsubscribe - <repo> <file pattern[s]>"
    )

def login_command(update, context):
    update.message.reply_text("Login with your GitHub account (TODO)")

def logout_command(update, context):
    update.message.reply_text("Logout from your GitHub account (TODO)")

def enable_command(update, context):
    update.message.reply_text("Now the service is enabled (TODO)")

def disable_command(update, context):
    update.message.reply_text("Now the service is disabled (TODO)")

def handle_message(update, context):
    text = str(update.message.text).lower()
    response = R.sample_responses(text)

    update.message.reply_text(response)

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

    dp.add_handler(MessageHandler(Filters.text, handle_message))

    updater.start_polling(1)
    updater.idle()

main()