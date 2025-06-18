LANG = "ru"
DB_PATH = "data/logs.db"
MAX_PAGES = 50
SETTINGS_PATH = "settings.json"

import json
import os

# 📦 Кэшируем настройки один раз
try:
    with open(os.path.join(os.path.dirname(__file__), SETTINGS_PATH), "r", encoding="utf-8") as f:
        SETTINGS = json.load(f)
except Exception as e:
    print(f"[config] Ошибка загрузки settings.json: {e}")
    SETTINGS = {}

# ✅ Сохраняем старую функцию на случай, если нужно перезагрузить вручную
def load_config():
    with open(os.path.join(os.path.dirname(__file__), SETTINGS_PATH), encoding="utf-8") as f:
        return json.load(f)
