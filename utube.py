import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pytube import YouTube
from pytube.exceptions import VideoUnavailable
import os

# Initialize the database
Base = declarative_base()
engine = create_engine('sqlite:///users.db')
Session = sessionmaker(bind=engine)
session = Session()

# Define the User model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True)
    videos_downloaded_480p = Column(Integer, default=0)
    videos_downloaded_720p = Column(Integer, default=0)
    videos_downloaded_1080p = Column(Integer, default=0)

# Create the database tables
Base.metadata.create_all(engine)

# Bot token
TOKEN = 'YOUR_BOT_TOKEN'
WEBHOOK_URL = 'https://your-service-url.onrender.com'
ADMIN_ID = '6826870863'

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def is_admin(user_id: str) -> bool:
    return user_id == ADMIN_ID

def get_user(telegram_id: str):
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    return user

def get_all_users():
    users = session.query(User).all()
    return users

def get_download_statistics():
    stats = {
        '480p': session.query(User.videos_downloaded_480p).count(),
        '720p': session.query(User.videos_downloaded_720p).count(),
        '1080p': session.query(User.videos_downloaded_1080p).count(),
    }
    return stats

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = str(update.effective_user.id)
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id)
        session.add(user)
        session.commit()
    await update.message.reply_text('Welcome! Please send me a YouTube link.')

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
        await update.message.reply_text('Please choose your preferred quality:', reply_markup=reply_markup)
    except VideoUnavailable:
        await update.message.reply_text('Invalid Link. Please send a valid YouTube link.')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    format_choice = query.data
    context.user_data['format'] = format_choice

    if format_choice == '2k':
        await query.edit_message_text(text="Only available for Premium Members.")
        return

    await query.edit_message_text(text=f"Selected format: {format_choice}. Downloading the video...")

    url = context.user_data['video_url']
    telegram_id = str(query.from_user.id)
    user = session.query(User).filter_by(telegram_id=telegram_id).first()

    try:
        yt = YouTube(url)
        if format_choice == '480p':
            stream = yt.streams.filter(res="480p").first()
            user.videos_downloaded_480p += 1
        elif format_choice == '720p':
            stream = yt.streams.filter(res="720p").first()
            user.videos_downloaded_720p += 1
        elif format_choice == '1080p':
            stream = yt.streams.filter(res="1080p").first()
            user.videos_downloaded_1080p += 1

        session.commit()

        video_file = stream.download()
        await query.message.reply_video(video=open(video_file, 'rb'), caption=f"Downloaded in {format_choice}")

    except Exception as e:
        await query.message.reply_text(f"An error occurred: {e}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(str(update.effective_user.id)):
        await update.message.reply_text("You do not have permission to access this command.")
        return

    stats = get_download_statistics()
    stats_message = (f"Download Statistics:\n"
                     f"480p: {stats['480p']} videos\n"
                     f"720p: {stats['720p']} videos\n"
                     f"1080p: {stats['1080p']} videos")
    await update.message.reply_text(stats_message)

async def user_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(str(update.effective_user.id)):
        await update.message.reply_text("You do not have permission to access this command.")
        return

    telegram_id = context.args[0] if context.args else None
    if not telegram_id:
        await update.message.reply_text("Please provide a Telegram ID.")
        return

    user = get_user(telegram_id)
    if user:
        user_info = (f"User ID: {user.telegram_id}\n"
                     f"480p Downloads: {user.videos_downloaded_480p}\n"
                     f"720p Downloads: {user.videos_downloaded_720p}\n"
                     f"1080p Downloads: {user.videos_downloaded_1080p}")
        await update.message.reply_text(user_info)
    else:
        await update.message.reply_text("User not found.")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("user_data", user_data))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, validate_link))
    application.add_handler(CallbackQueryHandler(button))

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get('PORT', 8443)),
        url_path=TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
    )

if __name__ == '__main__':
    main()