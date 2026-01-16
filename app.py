import telebot
import os
from PIL import Image
from flask import Flask, request

# --- الإعدادات ---
TOKEN = '7025810245:AAHgw3rhEcurbGTkpENcW2xOdAy8-0OtVvA'
ADMIN_ID = 5157796513  
DEVELOPER_USERNAME = "YYH3H" 

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# ملفات الخزن المؤقت
USERS_FILE = "users.txt"
REQUIRED_CHANNELS = "channels.txt"

# --- دالة التحقق من الاشتراك ---
def check_join(user_id):
    if not os.path.exists(REQUIRED_CHANNELS): return True
    with open(REQUIRED_CHANNELS, "r") as f:
        channels = f.read().splitlines()
    for ch in channels:
        try:
            status = bot.get_chat_member(ch, user_id).status
            if status == 'left': return False
        except: continue
    return True

# --- المسارات (Routes) ---
@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    return "Forbidden", 403

@app.route('/', methods=['GET'])
def home():
    return "Bot YYH3H is Running on Koyeb!", 200

# --- لوحة الإدارة ---
@bot.message_handler(commands=['admin'])
def admin_login(message):
    if message.from_user.id == ADMIN_ID:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📊 الإحصائيات", "📢 إذاعة")
        markup.add("🏠 القائمة الرئيسية")
        bot.send_message(message.chat.id, "✅ أهلاً مطور حسين، تم فتح اللوحة:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📊 الإحصائيات" and m.from_user.id == ADMIN_ID)
def stats(message):
    count = 0
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f: count = len(f.readlines())
    bot.reply_to(message, f"👥 عدد المشتركين: {count}")

# --- أوامر المستخدم ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not os.path.exists(USERS_FILE): open(USERS_FILE, "w").close()
    with open(USERS_FILE, "r+") as f:
        users = f.read().splitlines()
        if str(user_id) not in users: f.write(f"{user_id}\n")
    
    if not check_join(user_id):
        bot.send_message(message.chat.id, "⚠️ اشترك بقنوات البوت أولاً.")
        return

    bot.send_message(message.chat.id, f"أهلاً بك! أرسل الصور لتحويلها إلى PDF.\nالمطور: @{DEVELOPER_USERNAME}")

# --- تحويل الصور ---
user_photos = {}

@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    chat_id = message.chat.id
    if chat_id not in user_photos: user_photos[chat_id] = []
    
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    temp_name = f"img_{chat_id}_{len(user_photos[chat_id])}.jpg"
    with open(temp_name, 'wb') as f: f.write(downloaded_file)
    user_photos[chat_id].append(temp_name)
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("✅ تحويل الصور الآن", callback_data="done_pdf"))
    bot.reply_to(message, f"📥 استلمت الصورة {len(user_photos[chat_id])}.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "done_pdf")
def create_pdf(call):
    chat_id = call.message.chat.id
    if chat_id in user_photos and user_photos[chat_id]:
        bot.edit_message_text("⏳ جاري إنشاء PDF...", chat_id, call.message.message_id)
        pdf_path = f"file_{chat_id}.pdf"
        images = [Image.open(img).convert('RGB') for img in user_photos[chat_id]]
        images[0].save(pdf_path, save_all=True, append_images=images[1:], quality=100)
        with open(pdf_path, 'rb') as f:
            bot.send_document(chat_id, f, caption=f"✅ تم التحويل!\nالمطور: @{DEVELOPER_USERNAME}")
        for img in user_photos[chat_id]: os.remove(img)
        user_photos[chat_id] = []
        os.remove(pdf_path)

# --- التشغيل على Koyeb ---
if __name__ == '__main__':
    # Koyeb يحتاج تحديد الـ Port والـ Host
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
