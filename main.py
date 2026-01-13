import telebot
import requests
from flask import Flask
from threading import Thread

# --- الجزء المسؤول عن إبقاء البوت حياً 24 ساعة ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running! ✅"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ---------------------------------------------

# --- كود البوت ---
TOKEN = '7025810245:AAHAT8WtACQETfSOo6_3UtgrM4WLka-4QQs'
bot = telebot.TeleBot(TOKEN)

def get_tiktok_video(url):
    try:
        api_url = f"https://api.tiklydown.eu.org/api/download?url={url}"
        response = requests.get(api_url, timeout=20)
        data = response.json()
        return data.get('result', {}).get('video', {}).get('no_watermark')
    except:
        return None

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "أهلاً بك! البوت يعمل الآن بنظام 24/7 🚀")

@bot.message_handler(func=lambda m: "tiktok.com" in m.text)
def download(message):
    msg = bot.reply_to(message, "⏳ جاري جلب الفيديو...")
    link = get_tiktok_video(message.text)
    if link:
        bot.send_video(message.chat.id, link)
        bot.delete_message(message.chat.id, msg.message_id)
    else:
        bot.edit_message_text("❌ فشل التحميل.", message.chat.id, msg.message_id)

# --- تشغيل كل شيء معاً ---
if __name__ == "__main__":
    keep_alive()  # تشغيل خادم الويب ليراه UptimeRobot
    print("البوت بدأ العمل...")
    bot.polling(none_stop=True)
