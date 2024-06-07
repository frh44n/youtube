from flask import Flask, request, jsonify
import requests
import pytube

app = Flask(__name__)

# Telegram Bot API endpoint
TELEGRAM_API_URL = 'https://api.telegram.org/bot<7063619963:AAEFPnp3F7sePbM6ElHtTju1PQH_9B5_eCM>/sendMessage'

# Handler for incoming messages
@app.route('/', methods=['POST'])
def handle_message():
    data = request.json
    chat_id = data['message']['chat']['id']
    video_link = data['message']['text']
    
    # Download the YouTube video
    yt = pytube.YouTube(video_link)
    stream = yt.streams.first()
    stream.download()
    
    # Send the downloaded video to the user
    files = {'video': open('video.mp4', 'rb')}
    requests.post(TELEGRAM_API_URL, data={'chat_id': chat_id}, files=files)
    
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(port=5000)
