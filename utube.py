import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import pytube

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the bot token
TOKEN = '7063619963:AAEFPnp3F7sePbM6ElHtTju1PQH_9B5_eCM'

# Define the welcome message
WELCOME_MESSAGE = "Welcome to the best and most powerful Telegram bot for downloading YouTube videos."

# Define the available formats
FORMATS = ['mp3', '480p', '720p', '1080p', '2k']

# Function to handle the /start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(WELCOME_MESSAGE)
    show_options(update)

# Function to show format options
def show_options(update: Update) -> None:
    keyboard = [[InlineKeyboardButton(format, callback_data=format)] for format in FORMATS]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please select the format:', reply_markup=reply_markup)

# Function to handle button presses
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f"Selected option: {query.data}")
    download_video(update, query.data)

# Function to download the video
def download_video(update: Update, format: str) -> None:
    # Get the YouTube video link from the user
    video_link = update.message.text
    try:
        # Download the YouTube video
        yt = pytube.YouTube(video_link)
        stream = yt.streams.filter(res=format).first()
        stream.download()
        update.message.reply_text(f"Video downloaded in {format} format.")
    except Exception as e:
        update.message.reply_text("An error occurred while downloading the video.")

def main() -> None:
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, show_options))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
