import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from PIL import Image

# التوكن الخاص بك
TOKEN = "7025810245:AAHX6TX7KWU53n5uwRRUYauDYDGb01DIhYg"

# مجلد مؤقت للصور
IMAGE_DIR = "images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 أهلاً بك! ارسل الصور التي تريد تحويلها، وبعد الانتهاء أرسل أمر /pdf"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()

    user_id = update.message.from_user.id
    user_folder = os.path.join(IMAGE_DIR, str(user_id))
    os.makedirs(user_folder, exist_ok=True)

    # تحديد رقم الصورة بناءً على الموجود في المجلد
    count = len(os.listdir(user_folder)) + 1
    image_path = os.path.join(user_folder, f"{count}.jpg")
    
    await file.download_to_drive(image_path)
    await update.message.reply_text(f"✅ تم حفظ الصورة رقم {count}")

async def make_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_folder = os.path.join(IMAGE_DIR, str(user_id))

    if not os.path.exists(user_folder) or not os.listdir(user_folder):
        await update.message.reply_text("❌ لم ترسل أي صور بعد!")
        return

    msg = await update.message.reply_text("🔄 جاري إنشاء ملف PDF... انتظر قليلاً")

    try:
        images = []
        # ترتيب الملفات رقمياً
        files = sorted(os.listdir(user_folder), key=lambda x: int(x.split(".")[0]))

        for file_name in files:
            img_path = os.path.join(user_folder, file_name)
            img = Image.open(img_path).convert("RGB")
            images.append(img)

        pdf_path = f"PDF_{user_id}.pdf"
        images[0].save(pdf_path, save_all=True, append_images=images[1:])

        with open(pdf_path, "rb") as pdf_file:
            await update.message.reply_document(document=pdf_file, filename="Your_Images.pdf")

        # تنظيف الذاكرة والملفات
        for f in os.listdir(user_folder):
            os.remove(os.path.join(user_folder, f))
        os.rmdir(user_folder)
        os.remove(pdf_path)
        await msg.delete()
            
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء المعالجة: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 التعليمات:\n1️⃣ ارسل الصور واحدة تلو الأخرى.\n2️⃣ اكتب أمر /pdf للتحويل.\n3️⃣ سيقوم البوت بإرسال الملف وحذف الصور القديمة."
    )

def main():
    # بناء التطبيق
    app = ApplicationBuilder().token(TOKEN).build()

    # إضافة الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pdf", make_pdf))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("البوت يعمل الآن بنجاح...")
    app.run_polling()

if __name__ == "__main__":
    main()
