from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, CallbackQueryHandler
from telegram.ext.filters import Filters
import pytube
import logging

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the bot token from the environment variable
TOKEN = os.environ.get('BOT_TOKEN')

# Function to handle the /start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome to the best and most powerful Telegram bot for downloading YouTube videos.")
    show_options(update)

# Function to show format options
def show_options(update: Update) -> None:
    keyboard = [[format] for format in ['mp3', '480p', '720p', '1080p', '2k']]
    update.message.reply_text('Please select the format:', reply_markup=keyboard)

# Function to handle button presses
def handle_message(update: Update, context: CallbackContext) -> None:
    download_video(update)

# Function to download the video
def download_video(update: Update) -> None:
    # Get the YouTube video link from the user
    video_link = update.message.text
    try:
        # Download the YouTube video
        yt = pytube.YouTube(video_link)
        stream = yt.streams.first()
        stream.download()
        update.message.reply_text(f"Video downloaded.")
    except Exception as e:
        update.message.reply_text("An error occurred while downloading the video.")

def main() -> None:
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
