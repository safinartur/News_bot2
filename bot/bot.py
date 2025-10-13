import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
from typing import Optional
import hashlib

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# --- Этапы диалога ---
TITLE, BODY, IMAGE, CONFIRM = range(4)

# --- Загрузка переменных окружения ---
load_dotenv()

API_BASE = os.getenv("BACKEND_API_BASE", "http://127.0.0.1:8000/api")
API_KEY = os.getenv("API_SHARED_KEY")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MOD_IDS = set([int(x) for x in os.getenv("MODERATOR_IDS", "").split(",") if x.strip().isdigit()])
DEFAULT_TAGS = [t.strip() for t in os.getenv("DEFAULT_TAGS", "").split(",") if t.strip()]
WEBHOOK_URL = os.getenv("BOT_WEBHOOK_URL")  # например: https://news-bot.onrender.com/webhook
PORT = int(os.getenv("PORT", "8443"))

# --- Requests с retry ---
retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry_strategy)
requests_session = requests.Session()
requests_session.mount("http://", adapter)
requests_session.mount("https://", adapter)


# --- Проверка прав модератора ---
def is_authorized(user_id: int) -> bool:
    return not MOD_IDS or user_id in MOD_IDS


# --- /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("⛔ Доступ только для модераторов.")
        return ConversationHandler.END
    await update.message.reply_text("👋 Отправьте заголовок новости.")
    return TITLE


# --- Получение заголовка ---
async def got_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["title"] = update.message.text.strip()
    await update.message.reply_text("📝 Теперь пришлите текст новости (Markdown разрешён).")
    return BODY


# --- Получение текста ---
async def got_body(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["body"] = update.message.text or update.message.caption or ""
    await update.message.reply_text("📷 Пришлите изображение (как фото) или /skip чтобы пропустить.")
    return IMAGE


# --- Пропуск фото ---
async def skip_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["photo_file"] = None
    return await preview(update, context)


# --- Получение фото ---
async def got_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    photo_path = await file.download_to_drive(custom_path="upload.jpg")
    context.user_data["photo_file"] = photo_path
    return await preview(update, context)


# --- Предпросмотр ---
async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = context.user_data.get("title", "")
    body = context.user_data.get("body", "")
    await update.message.reply_text(
        f"Предпросмотр:\n\n<b>{title}</b>\n\n{body}\n\nОтправить? /confirm или /cancel",
        parse_mode="HTML",
    )
    return CONFIRM


# --- Публикация ---
async def publish(update: Update, context: ContextTypes.DEFAULT_TYPE, photo_file: Optional[str]):
    print("📤 Публикация новости...")
    try:
        # Проверяем backend
        ping_url = f"{API_BASE}/posts/?page=1"
        ping_resp = requests.get(ping_url, timeout=10)
        if not ping_resp.ok:
            await update.message.reply_text(
                f"⚠️ Backend ответил ошибкой ({ping_resp.status_code}). Попробуй позже."
            )
            return

        # Отправляем POST
        data = {
            "title": context.user_data.get("title", "(без названия)"),
            "body": context.user_data.get("body", "(без текста)"),
            "tag_slugs": DEFAULT_TAGS,
        }
        files = {"cover": open(photo_file, "rb")} if photo_file else None
        headers = {"X-API-KEY": API_KEY}

        r = requests_session.post(f"{API_BASE}/posts/", data=data, files=files, headers=headers, timeout=(10, 30))
        if files:
            files["cover"].close()

        if r.ok:
            post = r.json()
            FRONTEND_BASE = os.getenv("FRONTEND_BASE", API_BASE.replace("/api", ""))
            url = f"{FRONTEND_BASE}/#/post/{post['slug']}"
            await update.message.reply_text(f"✅ Опубликовано успешно:\n{url}")
        else:
            await update.message.reply_text(f"❌ Ошибка публикации ({r.status_code}): {r.text[:400]}")

    except Exception as e:
        print(f"💥 Ошибка в publish(): {e}")
        await update.message.reply_text(f"💥 Ошибка публикации: {e}")


# --- Подтверждение ---
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = hashlib.sha256(
        (context.user_data.get("title", "") + "|" + context.user_data.get("body", "")).encode()
    ).hexdigest()

    if context.application.bot_data.get(key):
        await update.message.reply_text("Похоже, эта новость уже публиковалась недавно. Отмена.")
        return ConversationHandler.END

    await publish(update, context, photo_file=context.user_data.get("photo_file"))
    context.application.bot_data[key] = True
    return ConversationHandler.END


# --- Отмена ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отмена публикации.")
    return ConversationHandler.END


# --- /status ---
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        r = requests.get(f"{API_BASE}/posts/?page=1", timeout=8)
        if r.ok:
            await update.message.reply_text("✅ Backend доступен.")
        else:
            await update.message.reply_text(f"⚠️ Backend ответил ошибкой ({r.status_code}).")
    except Exception as e:
        await update.message.reply_text(f"🟥 Backend недоступен: {e}")


# --- Создание приложения ---
def build_app():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("new", start)],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_title)],
            BODY: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_body)],
            IMAGE: [
                CommandHandler("skip", skip_image),
                MessageHandler(filters.PHOTO, got_image),
            ],
            CONFIRM: [
                CommandHandler("confirm", confirm),
                CommandHandler("cancel", cancel),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(conv)
    return app


# --- Основной запуск (Webhook) ---
if __name__ == "__main__":
    print("🌐 Пробую разбудить backend...")
    try:
        requests.get(f"{API_BASE}/posts/?page=1", timeout=10)
    except Exception:
        print("⚠️ Backend пока недоступен")

    print("🤖 Запуск Telegram-бота через Webhook...")
    app = build_app()

    if not WEBHOOK_URL:
        raise ValueError("❌ BOT_WEBHOOK_URL не задан в .env!")

    print(f"🔗 Устанавливаю webhook: {WEBHOOK_URL}/{TOKEN}")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}",
    )
