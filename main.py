import os
import instaloader
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = os.environ.get("BOT_TOKEN", "ВАШ_ТОКЕН_СЮДА")

def start(update, context):
    update.message.reply_text("Привет! Отправь мне ссылку на пост или Reels из Instagram, и я скачаю видео/фото без водяных знаков.")

def handle_message(update, context):
    url = update.message.text
    if "instagram.com" not in url:
        update.message.reply_text("Отправь ссылку на Instagram")
        return
    
    update.message.reply_text("⏳ Скачиваю...")
    
    try:
        # Извлекаем короткий код (shortcode) из ссылки
        # Пример: https://www.instagram.com/p/Ctt5XupruCM/ -> Ctt5XupruCM
        shortcode = url.split("/")[-2]
        
        loader = instaloader.Instaloader()
        # Используем правильный метод from_shortcode
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        
        if not os.path.exists("download"):
            os.makedirs("download")
        
        loader.download_post(post, target="download")
        
        files = os.listdir("download")
        video_found = False
        photo_found = False
        
        for file in files:
            if file.endswith(".mp4"):
                with open(f"download/{file}", "rb") as f:
                    update.message.reply_video(f)
                video_found = True
                break
        
        if not video_found:
            for file in files:
                if file.endswith(".jpg") or file.endswith(".png"):
                    with open(f"download/{file}", "rb") as f:
                        update.message.reply_photo(f)
                    photo_found = True
                    break
        
        if not video_found and not photo_found:
            update.message.reply_text("Не удалось найти медиафайлы в этом посте")
        
        for file in os.listdir("download"):
            os.remove(f"download/{file}")
        os.rmdir("download")
        
    except Exception as e:
        update.message.reply_text(f"Ошибка: {str(e)}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
