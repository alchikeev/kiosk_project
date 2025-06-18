#!/bin/bash

PROJECT_DIR="$HOME/Desktop/1"
IMAGE_NAME="ubuntu:22.04"
CONTAINER_NAME="kiosk_container"

echo "▶️ Удаление предыдущего контейнера (если был)..."
docker rm -f $CONTAINER_NAME > /dev/null 2>&1

echo "▶️ Запуск Docker-контейнера: $CONTAINER_NAME"
docker run -d \
  --name $CONTAINER_NAME \
  -v "$PROJECT_DIR":/app \
  "$IMAGE_NAME" bash -c "
    apt update &&
    apt install -y python3 python3-pip &&
    pip3 install -r /app/kiosk_core/requirements.txt || true &&
    pip3 install -r /app/kiosk_web/requirements.txt || true &&
    export PYTHONPATH=/app &&
    cd /app && ./start_all.sh
"

sleep 2

echo "🪟 Открытие нового окна терминала для логов Docker..."
osascript <<EOF
tell application "Terminal"
    activate
    do script "docker logs -f $CONTAINER_NAME"
end tell
EOF

sleep 1

echo "🖥️ Запуск GUI на Mac из виртуального окружения..."
source "$PROJECT_DIR/kiosk_core/venv/bin/activate"

echo "📦 Установка зависимостей из requirements.txt..."
pip install -r "$PROJECT_DIR/kiosk_core/requirements.txt"

echo "🚀 Запуск GUI..."
python3 "$PROJECT_DIR/kiosk_core/run.py"

echo "✅ Все процессы запущены. Чтобы остановить: вручную закрой окно логов и останови контейнер:"
echo "    docker stop $CONTAINER_NAME"
