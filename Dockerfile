# Используем лёгкий образ с Python
FROM python:3.10-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    libcups2-dev \
    sane-utils \
    git \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем проект в контейнер
COPY . /app

# Устанавливаем зависимости Python
RUN pip install --upgrade pip
RUN pip install -r kiosk_core/requirements.txt

# Делаем скрипт исполняемым
RUN chmod +x /app/start_all.sh

# Стартовая команда при запуске контейнера
CMD ["bash", "/app/start_all.sh"]
