import os
import json
from config import LANG

LOCALE_DIR = os.path.join(os.path.dirname(__file__), "../../locales")

TRANSLATIONS = {}

def load_translations(lang_code):
    path = os.path.join(LOCALE_DIR, f"{lang_code}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки перевода для {lang_code}: {e}")
        return {}

def set_language(lang_code):
    global TRANSLATIONS
    TRANSLATIONS = load_translations(lang_code)

set_language(LANG)

def t(key):
    return TRANSLATIONS.get(key, key)