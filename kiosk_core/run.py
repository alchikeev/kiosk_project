import sys
import os

# Получаем абсолютный путь к директории, где находится run.py
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Добавляем корневую директорию в sys.path, если ее там еще нет
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from kiosk.gui.main import start_gui

if __name__ == "__main__":
    start_gui()
