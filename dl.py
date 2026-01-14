import telebot
import yt_dlp
import os
import time

# --- معلومات البوت ---
TOKEN = "7752772825:AAGoOFcJBnmGDVa7O2enp1v85KLK0Ssgxeo"
bot = telebot.TeleBot(TOKEN)

# دالة التحميل
def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4', # اسم الملف المؤقت
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 أهلاً بك في بوت تحميل حسين!\n\nأرسل لي أي رابط من (تيك توك، إنستا، يوتيوب) وسأقوم بتحميله لك فوراً.")

@bot.message_handler(func=lambda m: True)
def handle_links(message):
    url = message.text
    if "http" not in url:
        return

    msg = bot.reply_to(message, "⏳ جاري جلب الفيديو.. انتظر قليلاً")
    
    try:
        # تحميل الفيديو للسيرفر
        download_video(url)
        
        # إرسال الفيديو للمستخدم
        with open('video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video, caption="✅ تم التحميل بواسطة بوت حسين")
        
        # حذف الفيديو من السيرفر لتوفير المساحة
        os.remove('video.mp4')
        bot.delete_message(message.chat.id, msg.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"❌ عذراً، لا يمكن تحميل هذا الرابط حالياً.\nتأكد أن الحساب عام وليس خاصاً.", message.chat.id, msg.message_id)
        if os.path.exists('video.mp4'):
            os.remove('video.mp4')

if __name__ == "__main__":
    print("🛰️ Downloader Bot is Online...")
    bot.infinity_polling()
