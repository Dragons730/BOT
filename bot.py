import os
import instaloader
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN", "ВАШ_ТОКЕН_СЮДА")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне ссылку на пост или Reels из Instagram, и я скачаю видео/фото без водяных знаков.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "instagram.com" not in url:
        await update.message.reply_text("Отправь ссылку на Instagram")
        return
    
    await update.message.reply_text("⏳ Скачиваю...")
    
    try:
        loader = instaloader.Instaloader()
        post = instaloader.Post.from_url(loader.context, url)
        
        if post.is_video:
            loader.download_post(post, target="download")
            # Находим скачанный файл
            for file in os.listdir("download"):
                if file.endswith(".mp4"):
                    with open(f"download/{file}", "rb") as f:
                        await update.message.reply_video(f)
                    break
        else:
            loader.download_post(post, target="download")
            for file in os.listdir("download"):
                if file.endswith(".jpg") or file.endswith(".png"):
                    with open(f"download/{file}", "rb") as f:
                        await update.message.reply_photo(f)
                    break
        
        # Очищаем папку
        for file in os.listdir("download"):
            os.remove(f"download/{file}")
        os.rmdir("download")
        
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
