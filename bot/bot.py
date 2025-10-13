import os
import time
import hashlib
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
from telegram.error import NetworkError, TimedOut

print("📦 Загрузка Telegram Bot (PTB 20.8 Polling)")

# === Настройки окружения ===
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE = os.getenv("BACKEND_API_BASE", "http://127.0.0.1:8000/api")
API_KEY = os.getenv("API_SHARED_KEY")
MOD_IDS = {int(x) for x in os.getenv("MODERATOR_IDS", "").split(",") if x.strip().isdigit()}
DEFAULT_TAGS = [t.strip() for t in os.getenv("DEFAULT_TAGS", "").split(",") if t.strip()]

# === Подготовка requests с retry ===
retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry_strategy)
requests_session = requests.Session()
requests_session.mount("http://", adapter)
requests_session.mount("https://", adapter)

# === Этапы диалога ===
TITLE, BODY, IMAGE, CONFIRM = range(4)

# === Проверка прав ===
def is_authorized(user_id: int) -> bool:
    return not MOD_IDS or user_id in MOD_IDS


# === Команды ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("⛔ Доступ только для модераторов.")
        return ConversationHandler.END
    await update.message.reply_text("👋 Отправьте заголовок новости.")
    return TITLE


async def got_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["title"] = update.message.text.strip()
    await update.message.reply_text("📝 Теперь пришлите текст новости (Markdown разрешён).")
    return BODY


async def got_body(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["body"] = update.message.text or update.message.caption or ""
    await update.message.reply_text("📷 Пришлите изображение (или /skip чтобы пропустить).")
    return IMAGE


async def skip_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["photo_file"] = None
    return await preview(update, context)


async def got_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    path = await file.download_to_drive(custom_path="upload.jpg")
    context.user_data["photo_file"] = path
    return await preview(update, context)


async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = context.user_data.get("title", "")
    body = context.user_data.get("body", "")
    await update.message.reply_text(
        f"<b>{title}</b>\n\n{body}\n\nОтправить? /confirm или /cancel",
        parse_mode="HTML",
    )
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = hashlib.sha256(
        (context.user_data.get("title", "") + "|" + context.user_data.get("body", "")).encode()
    ).hexdigest()

    if context.application.bot_data.get(key):
        await update.message.reply_text("Похоже, эта новость уже публиковалась недавно.")
        return ConversationHandler.END

    await publish(update, context, context.user_data.get("photo_file"))
    context.application.bot_data[key] = True
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Публикация отменена.")
    return ConversationHandler.END


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        r = requests.get(f"{API_BASE}/posts/?page=1", timeout=8)
        if r.ok:
            await update.message.reply_text("✅ Backend доступен.")
        else:
            await update.message.reply_text(f"⚠️ Backend ответил ошибкой ({r.status_code}).")
    except Exception as e:
        await update.message.reply_text(f"🟥 Backend недоступен: {e}")


# === Публикация ===
async def publish(update: Update, context: ContextTypes.DEFAULT_TYPE, photo_file: Optional[str]):
    print("📤 Публикация новости...")
    try:
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
        await update.message.reply_text(f"💥 Ошибка публикации: {e}")


# === Приложение ===
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


# === Основной цикл ===
if __name__ == "__main__":
    import telegram
    print(f"📦 python-telegram-bot version: {telegram.__version__}")

    while True:
        try:
            app = build_app()
            print("🤖 Запуск Telegram-бота через polling...")
            app.run_polling(allowed_updates=Update.ALL_TYPES)
        except (NetworkError, TimedOut) as e:
            print(f"🌐 NetworkError: {e}. Повтор через 15 секунд...")
            time.sleep(15)
            continue
        except Exception as e:
            print(f"💥 Неожиданная ошибка: {e}. Перезапуск через 60 секунд...")
            time.sleep(60)
            continue
