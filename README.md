# Django + React новости с автопостингом из Telegram

## Быстрый старт (WSL Ubuntu)

### 1) Бэкенд
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # при необходимости поменяйте API_SHARED_KEY
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

### 2) Фронтенд
В новом окне терминала:
```bash
cd frontend
npm i
cp .env.example .env
npm run dev
```
Откройте http://127.0.0.1:5173

### 3) Телеграм-бот
```bash
cd bot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # заполните токен и MODERATOR_IDS
python bot.py
```
Команда `/new` — мастер публикации (заголовок → текст → опционально фото).
Бот отправляет POST на `/api/posts/` c ключом `X-API-KEY`.

## Структура API
- `GET /api/posts/?page=1&tag=<slug>`
- `GET /api/posts/<slug>/`
- `POST /api/posts/` (multipart): поля `title, body, tag_slugs[], cover(optional)`

## Продакшн (кратко)
- Настройте `ALLOWED_HOSTS`, DEBUG=0, SECRET_KEY и `API_SHARED_KEY` в `.env`
- Соберите фронтенд: `npm run build`, отдайте статику из любого веб-сервера (Nginx), а API — через Gunicorn/Uvicorn.
