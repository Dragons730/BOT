import os
import instaloader
import yt_dlp
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ChatMember, InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = os.environ.get("BOT_TOKEN", "8593561296:AAGeFVp3PrEqo8-5PqBDczAf4Roko3AuH7Q")
CHANNEL_ID = -1004331031762
CHANNEL_LINK = "https://t.me/+WTQG6VxcsZxjN2Uy"

def check_subscription(update, context):
    user_id = update.effective_user.id
    try:
        chat_member = context.bot.get_chat_member(CHANNEL_ID, user_id)
        if chat_member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.CREATOR]:
            return True
        return False
    except:
        return False

def start(update, context):
    if not check_subscription(update, context):
        keyboard = [
            [InlineKeyboardButton("📢 Подписаться на канал", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "❗ Для использования бота подпишись на наш канал\n\n"
            "После подписки нажми кнопку 'Проверить подписку'",
            reply_markup=reply_markup
        )
        return
    
    update.message.reply_text(
        "Привет! Я скачиваю видео и фото с Instagram и TikTok без водяных знаков!\n\n"
        "Просто отправь мне ссылку на пост, Reels или TikTok."
    )

def check_subscription_callback(update, context):
    query = update.callback_query
    query.answer()
    
    if check_subscription(update, context):
        query.edit_message_text(
            "✅ Подписка подтверждена!\n\n"
            "Теперь ты можешь использовать бота. Отправь мне ссылку на Instagram или TikTok."
        )
    else:
        keyboard = [
            [InlineKeyboardButton("📢 Подписаться на канал", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            "❗ Ты ещё не подписан на канал.\n\n"
            "Подпишись и нажми 'Проверить подписку'",
            reply_markup=reply_markup
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
    if not check_subscription(update, context):
        keyboard = [
            [InlineKeyboardButton("📢 Подписаться на канал", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "❗ Подпишись на наш канал\n\n"
            "После подписки нажми 'Проверить подписку'",
            reply_markup=reply_markup
        )
        return
    
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
    dp.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="check_sub"))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
