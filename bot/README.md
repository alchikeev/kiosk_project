# Telegram-базовый бот для вендинг-аппарата

## Функции:
- Приём PDF/DOCX по Telegram
- Определение киоска через QR-ссылку
- Хранение сессий
- Генерация QR

## Запуск:
1. Установи зависимости:
```
pip install -r requirements.txt
```

2. Запусти бота:
```
python3 -m bot.main
```

3. Для генерации QR:
```
python3 utils/qr_generator.py
```
