import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from PIL import Image

TOKEN = os.getenv("7025810245:AAHX6TX7KWU53n5uwRRUYauDYDGb01DIhYg")

# مجلد مؤقت للصور
IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 ارسل الصور وبعدين اكتب /pdf حتى احولهم إلى ملف PDF"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()

    user_id = update.message.from_user.id
    user_folder = os.path.join(IMAGE_DIR, str(user_id))
    os.makedirs(user_folder, exist_ok=True)

    image_path = os.path.join(user_folder, f"{len(os.listdir(user_folder)) + 1}.jpg")
    await file.download_to_drive(image_path)

    await update.message.reply_text("✅ تم حفظ الصورة")

async def make_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_folder = os.path.join(IMAGE_DIR, str(user_id))

    if not os.path.exists(user_folder) or not os.listdir(user_folder):
        await update.message.reply_text("❌ ماكو صور محفوظة")
        return

    images = []
    files = sorted(os.listdir(user_folder), key=lambda x: int(x.split(".")[0]))

    for file_name in files:
        img = Image.open(os.path.join(user_folder, file_name)).convert("RGB")
        images.append(img)

    pdf_path = f"{user_folder}.pdf"
    images[0].save(pdf_path, save_all=True, append_images=images[1:])

    await update.message.reply_document(document=open(pdf_path, "rb"))

    # تنظيف الملفات
    for f in os.listdir(user_folder):
        os.remove(os.path.join(user_folder, f))
    os.rmdir(user_folder)
    os.remove(pdf_path)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 الطريقة:\n"
        "1️⃣ ارسل الصور\n"
        "2️⃣ اكتب /pdf\n"
        "راح يطلعلك ملف PDF"
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pdf", make_pdf))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
