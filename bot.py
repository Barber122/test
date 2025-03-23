import telebot
import requests
from telebot import types

BOT_TOKEN = "7942525400:AAF3ZC8bUv7fgliusO1DVCfzuxgsZmez0gQ"
bot = telebot.TeleBot(BOT_TOKEN)

owner_id = None
media_storage = {}

def download_file(file_id):
    try:
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        response = requests.get(file_url)
        if response.status_code == 200:
            return response.content
        else:
            return None
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None

@bot.message_handler(func=lambda message: message.text == "This bot is now connected to your business account.")
def handle_business_connection(message):
    global owner_id
    owner_id = message.from_user.id
    bot.send_message(owner_id, "Bot connected successfully!")

@bot.message_handler(content_types=['photo', 'video'])
def handle_media(message):
    if getattr(message, 'view_once', False) and (message.photo or message.video):
        if message.photo:
            file_id = message.photo[-1].file_id
            media_type = 'photo'
        elif message.video:
            file_id = message.video.file_id
            media_type = 'video'
        else:
            return
        media_data = download_file(file_id)
        if media_data:
            media_storage[message.message_id] = {'type': media_type, 'data': media_data}
            print(f"Saved {media_type} with message_id {message.message_id}")
        else:
            print(f"Failed to save {media_type} with message_id {message.message_id}")

@bot.message_handler(content_types=['text'])
def handle_owner_request(message):
    if owner_id and message.from_user.id == owner_id and 'reply_to_message' in dir(message):
        original_message_id = getattr(message, 'reply_to_message').message_id
        if original_message_id in media_storage:
            media_info = media_storage[original_message_id]
            if media_info:
                media_type = media_info['type']
                media_data = media_info['data']
                if media_type == 'photo':
                    bot.send_photo(owner_id, media_data)
                elif media_type == 'video':
                    bot.send_video(owner_id, media_data)
                bot.send_message(owner_id, "Here's your saved media!")
                del media_storage[original_message_id]
            else:
                bot.send_message(owner_id, "No saved media found for this message.")
    else:
        pass

if __name__ == "__main__":
    bot.infinity_polling()