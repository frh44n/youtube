import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from pytube import YouTube
from pytube.exceptions import VideoUnavailable
import os

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Bot token
TOKEN = '7063619963:AAEFPnp3F7sePbM6ElHtTju1PQH_9B5_eCM'

def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    update.message.reply_text('Welcome! Please send me a YouTube link.')

async def validate_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    try:
        yt = YouTube(url)
        context.user_data['video_url'] = url
        keyboard = [
            [InlineKeyboardButton("480p", callback_data='480p')],
            [InlineKeyboardButton("720p", callback_data='720p')],
            [InlineKeyboardButton("1080p", callback_data='1080p')],
            [InlineKeyboardButton("2K", callback_data='2k')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Please choose your preferred quality:', reply_markup=reply_markup)
    except VideoUnavailable:
        update.message.reply_text('Invalid Link. Please send a valid YouTube link.')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    format_choice = query.data
    context.user_data['format'] = format_choice

    if format_choice == '2k':
        query.edit_message_text(text="Only available for Premium Members.")
        return

    query.edit_message_text(text=f"Selected format: {format_choice}. Downloading the video...")

    url = context.user_data['video_url']

    try:
        yt = YouTube(url)
        if format_choice == '480p':
            stream = yt.streams.filter(res="480p").first()
        elif format_choice == '720p':
            stream = yt.streams.filter(res="720p").first()
        elif format_choice == '1080p':
            stream = yt.streams.filter(res="1080p").first()

        video_file = stream.download()
        query.message.reply_video(video=open(video_file, 'rb'), caption=f"Downloaded in {format_choice}")

    except Exception as e:
        query.message.reply_text(f"An error occurred: {e}")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, validate_link))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()

if __name__ == '__main__':
    main()
