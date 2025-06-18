import sqlite3
import os
from datetime import datetime
import json

# Предполагается, что DB_PATH определен в config.py
# Пример: DB_PATH = "logs.db"
DB_PATH = "data/logs.db"

def init_db():
    """
    Инициализирует базу данных для логирования. Создает таблицу app_logs, если она не существует.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_code TEXT NOT NULL,
                logged_at TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                page_count INTEGER NOT NULL,
                payment_status TEXT NOT NULL,
                execution_status TEXT NOT NULL
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
        # Здесь можно добавить более серьезную обработку ошибки,
        # например, генерацию исключения или отправку уведомления.
    finally:
        if conn:
            conn.close()


def log_event(operation_code, operation_type, page_count, payment_status, execution_status):
    """
    Логирует событие в базу данных.

    Args:
        operation_code (str): Индивидуальный код операции (например, "TON-001_123456789").
        operation_type (str): Тип операции ("copy", "scan", "print").
        page_count (int): Количество листов.
        payment_status (str): Статус оплаты.
        execution_status (str): Статус выполнения.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO app_logs (operation_code, logged_at, operation_type, page_count, payment_status, execution_status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (operation_code, datetime.now().isoformat(), operation_type, page_count, payment_status, execution_status))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error logging event: {e}")
        # Здесь также нужна обработка ошибки.  Можно попробовать повторить запись,
        # или записать ошибку в отдельный лог-файл.
    finally:
        if conn:
            conn.close()



def get_logs():
    """
    Извлекает все логи из базы данных, отсортированные по времени.

    Returns:
        list: Список кортежей, где каждый кортеж представляет собой запись лога.
              Возвращает пустой список в случае ошибки.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM app_logs ORDER BY logged_at DESC")
        logs = cursor.fetchall()
        return logs
    except sqlite3.Error as e:
        print(f"Error retrieving logs: {e}")
        return [] # Return empty list on error
    finally:
        if conn:
            conn.close()

def get_device_id():
    """
    Извлекает ID устройства из файла settings.json.

    Returns:
        str: ID устройства или "UNKNOWN_DEVICE", если файл не найден или ID отсутствует.
    """
    try:
        with open("settings.json", "r", encoding="utf-8") as f:
            settings = json.load(f)
            return settings.get("device_id", "UNKNOWN_DEVICE")
    except FileNotFoundError:
        print("settings.json not found")
        return "UNKNOWN_DEVICE"
    except json.JSONDecodeError:
        print("Invalid JSON in settings.json")
        return "UNKNOWN_DEVICE"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "UNKNOWN_DEVICE"

if __name__ == '__main__':
    init_db()
    # Пример использования
    device_id = get_device_id()
    operation_code = f"{device_id}_12345"  # Пример кода операции
    log_event(operation_code, "print", 1, "paid", "completed")
    log_event(operation_code, "scan", 2, "free", "pending")
    logs = get_logs()
    for log in logs:
        print(log)