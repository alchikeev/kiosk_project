#!/bin/bash

# Путь к проекту (внутри Docker он смонтирован как /app)
PROJECT_DIR=/app

# Временная директория для FIFO-файлов
FIFO_DIR="/tmp/kiosk_fifos_$$"
mkdir -p "$FIFO_DIR"

# Создаем именованные каналы
mkfifo "$FIFO_DIR/flask_fifo"
mkfifo "$FIFO_DIR/bot_fifo"
mkfifo "$FIFO_DIR/web_fifo"

# Обработчик завершения
cleanup() {
    echo "Завершение всех фоновых процессов и очистка..."
    pkill -TERM -P $$
    sleep 2
    pkill -KILL -P $$
    rm -rf "$FIFO_DIR"
    echo "Все фоновые процессы завершены и ресурсы очищены."
    exit 0
}
trap cleanup TERM INT EXIT

echo "=================================================="
echo "Запуск серверных приложений: $(date)"
echo "GUI вендинга запускается отдельно на Mac."
echo "=================================================="

# Flask API
echo "Запуск Flask API..."
(cd "$PROJECT_DIR/kiosk_core" && python3 -u kiosk_api.py 2>&1 | sed 's/^/Flask: /' > "$FIFO_DIR/flask_fifo") &
FLASK_PID=$!
echo "Flask API PID: $FLASK_PID"

# Telegram-бот
echo "Запуск Telegram-бота..."
(cd "$PROJECT_DIR/bot" && python3 -u -m bot.bot.main 2>&1 | sed 's/^/Bot: /' > "$FIFO_DIR/bot_fifo") &
BOT_PID=$!
echo "Бот PID: $BOT_PID"

# Web-интерфейс
echo "Запуск Web-интерфейса..."
(cd "$PROJECT_DIR/kiosk_web" && python3 -u -m app 2>&1 | sed 's/^/Web: /' > "$FIFO_DIR/web_fifo") &
WEB_PID=$!
echo "Web-интерфейс PID: $WEB_PID"

# tail всех логов
echo "--------------------------------------------------"
echo "Все серверные компоненты запущены."
echo "GUI запускай вручную на Mac: python3 run.py"
echo "--------------------------------------------------"
echo "PID Flask API: $FLASK_PID"
echo "PID Telegram-бот: $BOT_PID"
echo "PID Web-интерфейс: $WEB_PID"

(tail -f "$FIFO_DIR/flask_fifo" "$FIFO_DIR/bot_fifo" "$FIFO_DIR/web_fifo") &
TAIL_PID=$!
echo "PID процесса tail: $TAIL_PID"

wait $TAIL_PID
