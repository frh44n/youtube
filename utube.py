from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
import requests

# Function to handle start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! Send me an Instagram reel link and I will download it for you.')

# Function to handle messages
def echo(update: Update, context: CallbackContext) -> None:
    reel_link = update.message.text
    # Assuming you have a function to download Instagram reels
    download_reel(reel_link)
    update.message.reply_text('Reel downloaded successfully!')

# Function to download Instagram reel
def download_reel(link):
    # Implement your code to download the reel here
    pass

# Main function
def main():
    # Set up the Telegram bot
    updater = Updater("7063619963:AAEFPnp3F7sePbM6ElHtTju1PQH_9B5_eCM")
    dispatcher = updater.dispatcher

    # Handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
