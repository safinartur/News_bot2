# Telegram bot
```bash
cd bot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # заполните
python bot.py
```
Команда /new запускает мастера публикации. Список разрешённых модераторов — `MODERATOR_IDS`.
