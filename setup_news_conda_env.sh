#!/usr/bin/env bash
# ============================================================
# setup_clean_env.sh — Чистая установка проекта Django+React+Bot
# ============================================================
set -e

ENV_NAME="news_clean"
PYTHON_VER="3.11"
NODE_VER="20"

echo "=== [1/7] Проверка Conda ==="
if ! command -v conda &>/dev/null; then
  echo "❌ Conda не найдена. Установи Miniconda или Anaconda и перезапусти скрипт."
  exit 1
fi

echo "=== [2/7] Создаю новую среду $ENV_NAME ==="
conda create -y -n "$ENV_NAME" python="$PYTHON_VER"

echo "=== [3/7] Активирую среду ==="
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

echo "=== [4/7] Устанавливаю Node.js (через conda, без root) ==="
conda install -y -c conda-forge nodejs="$NODE_VER"

echo "=== [5/7] Устанавливаю Python-зависимости ==="
cd backend
pip install -r requirements.txt
cd ../bot
pip install -r requirements.txt
cd ..

echo "=== [6/7] Устанавливаю JS-зависимости ==="
cd frontend
rm -rf node_modules package-lock.json
npm install --ignore-scripts
cd ..

echo "=== [7/7] Создаю .env файлы ==="
for d in backend bot frontend; do
  if [ -f "$d/.env.example" ] && [ ! -f "$d/.env" ]; then
    cp "$d/.env.example" "$d/.env"
    echo "Создан $d/.env"
  fi
done

echo ""
echo "✅ Всё готово! Среда '$ENV_NAME' создана и проект собран."
echo ""
echo "Запуск:"
echo "  conda activate $ENV_NAME"
echo "  # Терминал 1 (бэкенд)"
echo "  cd backend && python manage.py runserver 0.0.0.0:8000"
echo ""
echo "  # Терминал 2 (фронтенд)"
echo "  cd frontend && npm run dev"
echo ""
echo "  # Терминал 3 (бот)"
echo "  cd bot && python bot.py"
echo ""
echo "Сайт: http://localhost:5173"
echo "API:  http://localhost:8000/api/posts/"
