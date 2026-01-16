import telebot
import subprocess
import os
import sys
import time
import threading
import logging
import platform
import json
import hashlib
import secrets
import psutil  # مكتبة مهمة لمعلومات النظام
from datetime import datetime
from telebot import types
from flask import Flask, request

# --- الإعدادات الأساسية ---
bot_token = "6082089576:AAFNq3fveHBHW3Hr56BS1QPlGEzFZHVtqCo"
ADMIN_IDS = [5157796513]  
bot = telebot.TeleBot(bot_token, threaded=False)
app = Flask(__name__)

bot_start_time = time.time()
active_sessions = {}

# --- إعدادات السيرفر (Flask) للـ Webhook ---
@app.route('/')
def index():
    return "Server is Running!"

@app.route(f'/{bot_token}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# --- دوال معلومات النظام ---
def get_server_stats():
    try:
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        uptime = time.strftime("%H:%M:%S", time.gmtime(time.time() - bot_start_time))
        
        stats = f"🖥 **حالة الخادم الحالية:**\n\n"
        stats += f"✅ النظام: {platform.system()} {platform.release()}\n"
        stats += f"🧠 الذاكرة: {mem.percent}% ({mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB)\n"
        stats += f"💾 التخزين: {disk.percent}% ({disk.free // (1024**3)}GB فرغ)\n"
        stats += f"⏳ مدة التشغيل: {uptime}\n"
        stats += f"🕒 الوقت: {datetime.now().strftime('%H:%M:%S')}"
        return stats
    except:
        return "⚠️ تعذر جلب إحصائيات النظام."

# --- لوحة التحكم (الأزرار) ---
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📊 حالة الخادم", callback_data="stats"),
        types.InlineKeyboardButton("📂 الملفات", callback_data="list_files"),
        types.InlineKeyboardButton("⚙️ معلومات النظام", callback_data="sys_info"),
        types.InlineKeyboardButton("📝 السجلات", callback_data="logs")
    )
    return markup

# --- معالجة الأوامر ---
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ نعتذر، هذا البوت مخصص للمطور فقط.")
        return
    
    welcome = f"🚀 أهلاً بك حسين في لوحة إدارة السيرفر المتقدمة.\n\nاستخدم الأزرار أدناه للتحكم:"
    bot.reply_to(message, welcome, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "stats":
        bot.edit_message_text(get_server_stats(), call.message.chat.id, call.message.message_id, reply_markup=main_menu())
    elif call.data == "sys_info":
        info = f"ℹ️ **تفاصيل النظام:**\n\nالمعالج: {platform.processor()}\nاللغة: Python {platform.python_version()}\nالنود: {platform.node()}"
        bot.answer_callback_query(call.id, "تم جلب المعلومات")
        bot.send_message(call.message.chat.id, info)

# --- تشغيل البوت والسيرفر ---
def run_bot():
    bot.remove_webhook()
    bot.infinity_polling()

if __name__ == "__main__":
    # إذا كنت تستخدم Koyeb أو Render يفضل تفعيل الـ Webhook
    # threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000)).start()
    print("البوت يعمل الآن...")
    bot.infinity_polling()
