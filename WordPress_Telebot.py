import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

# ================= CONFIG =================
WP_URL = "https://artursafin05032003-nhbzi.wordpress.com"               # адрес сайта без слеша в конце
WP_USER = "your_wp_username"                 # логин WordPress
WP_APP_PASSWORD = "abcd efgh ijkl mnop"      # пароль приложения
CATEGORY_ID = 3                              # ID категории "Новости о котах"
BOT_TOKEN = "ТОКЕН_ТЕЛЕГРАМ_БОТА"           # токен от BotFather
# ==========================================

# --------- 1. Старт -----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Привет! 🐱 Я помогу опубликовать новость о котах.\n\n"
        "Отправь заголовок новости:"
    )
    context.user_data["step"] = "title"

# --------- 2. Приём текста ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")

    # Заголовок
    if step == "title":
        context.user_data["title"] = update.message.text
        context.user_data["step"] = "content"
        await update.message.reply_text("Отлично! Теперь пришли текст новости:")
        return

    # Текст новости
    elif step == "content":
        context.user_data["content"] = update.message.text
        context.user_data["step"] = "media"
        await update.message.reply_text(
            "Хорошо! Пришли фото или видео (или напиши 'пропустить'):"
        )
        return

    # Если пользователь решил пропустить медиа
    elif step == "media" and update.message.text.lower() == "пропустить":
        context.user_data["step"] = "tags"
        await update.message.reply_text("Добавь теги через запятую (например: милота, пушистик):")
        return

    # Теги
    elif step == "tags":
        tags_text = update.message.text
        tags = [t.strip() for t in tags_text.split(",") if t.strip()]
        context.user_data["tags"] = tags
        await publish_to_wordpress(update, context)
        return

# --------- 3. Приём фото/видео ----------
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")

    if step == "media":
        # получаем файл из Telegram
        file = None
        filename = None
        if update.message.photo:
            file = await update.message.photo[-1].get_file()
            filename = "photo.jpg"
        elif update.message.video:
            file = await update.message.video.get_file()
            filename = "video.mp4"

        if file:
            temp_path = f"/tmp/{filename}"
            await file.download_to_drive(temp_path)

            with open(temp_path, "rb") as f:
                headers = {"Content-Disposition": f'attachment; filename={filename}'}
                auth = (WP_USER, WP_APP_PASSWORD)
                res = requests.post(f"{WP_URL}/wp-json/wp/v2/media",
                                    headers=headers, auth=auth,
                                    files={"file": f})
            if res.status_code == 201:
                media_id = res.json()["id"]
                context.user_data["media_id"] = media_id
                await update.message.reply_text("✅ Медиа успешно загружено!")
            else:
                await update.message.reply_text("⚠️ Не удалось загрузить медиа.")

        context.user_data["step"] = "tags"
        await update.message.reply_text("Теперь добавь теги через запятую:")
        return

# --------- 4. Публикация ----------
async def publish_to_wordpress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = context.user_data.get("title")
    content = context.user_data.get("content")
    tags_list = context.user_data.get("tags", [])
    media_id = context.user_data.get("media_id")

    # создаём (или находим) теги по API
    auth = (WP_USER, WP_APP_PASSWORD)
    tag_ids = []
    for tag in tags_list:
        r = requests.get(f"{WP_URL}/wp-json/wp/v2/tags?search={tag}", auth=auth)
        if r.ok and r.json():
            tag_ids.append(r.json()[0]["id"])
        else:
            r2 = requests.post(f"{WP_URL}/wp-json/wp/v2/tags", auth=auth, json={"name": tag})
            if r2.ok:
                tag_ids.append(r2.json()["id"])

    post_data = {
        "title": title,
        "content": content,
        "status": "pending",       # на модерации
        "categories": [CATEGORY_ID],
        "tags": tag_ids
    }
    if media_id:
        post_data["featured_media"] = media_id

    res = requests.post(f"{WP_URL}/wp-json/wp/v2/posts", auth=auth, json=post_data)

    if res.status_code == 201:
        post = res.json()
        await update.message.reply_text(
            f"✅ Новость отправлена на модерацию!\n"
            f"Заголовок: {title}\n"
            f"Предпросмотр: {post['link']}"
        )
    else:
        await update.message.reply_text("❌ Ошибка при отправке в WordPress.")
    context.user_data.clear()

# --------- Основной запуск ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    print("🤖 Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
