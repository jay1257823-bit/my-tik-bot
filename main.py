import requests
import random
import time
import threading
from fake_useragent import UserAgent

# --- بياناتك المضافة بنجاح ---
TOKEN = "7025810245:AAHgw3rhEcurbGTkpENcW2xOdAy8-0OtVvA"
ID = "5157796513"
# ----------------------

ua = UserAgent()
chars = "abcdefghijklmnopqrstuvwxyz0123456789"

def send_hit(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={ID}&text={msg}"
    try: 
        requests.get(url)
    except: 
        pass

def check_telegram():
    while True:
        user = "".join(random.choices(chars, k=5))
        try:
            req = requests.get(f"https://t.me/{user}", headers={'User-Agent': ua.random}).text
            if 'tgme_username_info' not in req:
                send_hit(f"🔹 صيد تليجرام جديد: @{user}")
        except: 
            pass
        time.sleep(10)

def check_insta_tiktok():
    while True:
        user = "".join(random.choices(chars, k=6))
        # فحص انستا
        try:
            if requests.get(f"https://www.instagram.com/{user}/", headers={'User-Agent': ua.random}).status_code == 404:
                send_hit(f"📸 متاح انستا: {user}")
        except: 
            pass
        # فحص تيك توك
        try:
            if requests.get(f"https://www.tiktok.com/@{user}", headers={'User-Agent': ua.random}).status_code == 404:
                send_hit(f"🎵 متاح تيك توك: {user}")
        except: 
            pass
        time.sleep(15)

print("--- Hunter Started 24/7 for Hussein ---")
threading.Thread(target=check_telegram).start()
threading.Thread(target=check_insta_tiktok).start()
