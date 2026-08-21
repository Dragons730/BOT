import os
import instaloader
import yt_dlp
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = os.environ.get("BOT_TOKEN", "ВАШ_ТОКЕН_СЮДА")

def start(update, context):
    update.message.reply_text(
        "Привет! Я скачиваю видео и фото с Instagram и TikTok без водяных знаков!\n\n"
        "Просто отправь мне ссылку на пост, Reels или TikTok."
    )

def download_tiktok(url):
    ydl_opts = {
        'outtmpl': 'download/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def handle_message(update, context):
    url = update.message.text
    update.message.reply_text("⏳ Скачиваю...")
    
    if "tiktok.com" in url:
        try:
            if not os.path.exists("download"):
                os.makedirs("download")
            
            video_path = download_tiktok(url)
            
            if video_path and os.path.exists(video_path):
                with open(video_path, "rb") as f:
                    update.message.reply_video(f)
                
                os.remove(video_path)
                os.rmdir("download")
            else:
                update.message.reply_text("Не удалось скачать видео с TikTok. Попробуй другую ссылку.")
        except Exception as e:
            update.message.reply_text(f"Ошибка при скачивании TikTok: {str(e)}")
        return
    
    if "instagram.com" in url:
        try:
            shortcode = url.split("/")[-2]
            loader = instaloader.Instaloader()
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
            update.message.reply_text(f"Ошибка Instagram: {str(e)}")
        return
    
    update.message.reply_text("Отправь ссылку на Instagram или TikTok")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
