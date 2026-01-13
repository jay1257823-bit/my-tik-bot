import telebot
import requests
from flask import Flask
from threading import Thread

# --- 1. إعداد سيرفر وهمي لضمان بقاء البوت حياً على Render ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running! ✅"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. إعدادات البوت والتوكن ---
TOKEN = '7025810245:AAGqdKWE0F5lbfNbhra-3Xi5JG03MRxTQT0'
bot = telebot.TeleBot(TOKEN)

# دالة جلب الفيديو من TikTok
def get_tiktok_video(url):
    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        response = requests.get(api_url, timeout=15).json()
        
        if response.get('code') == 0:
            video_link = response['data']['play']
            title = response['data'].get('title', 'TikTok Video')
            return video_link, title
        return None, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None

# --- 3. أوامر البوت ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"أهلاً بك يا {message.from_user.first_name} في بوت تحميل تيك توك!\n\nأرسل لي أي رابط الآن وسأقوم بتحميله لك بدون علامة مائية 🎬")

@bot.message_handler
