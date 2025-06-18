from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt
import os
import shutil

from kiosk.utils.translate import t

class SendScannedFileWidget(QWidget):
    def __init__(self, parent, file_path):
        super().__init__(parent)
        self.parent = parent
        self.file_path = file_path

        self.setLayout(self.build_ui())

    def build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        # Заголовок
        nav_layout = QHBoxLayout()
        btn_back = QPushButton("← " + t("back"))
        btn_back.clicked.connect(self.parent.show_main_menu)
        title = QLabel(t("send_scanned_file"))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        nav_layout.addWidget(btn_back)
        nav_layout.addWidget(title)
        nav_layout.addStretch()
        layout.addLayout(nav_layout)

        info = QLabel(f"Файл отсканирован и готов к отправке.")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

        # Кнопка: сохранить на флешку
        usb_btn = QPushButton("💾 Сохранить на флешку")
        usb_btn.clicked.connect(self.save_to_usb)
        layout.addWidget(usb_btn)

        # Кнопка: Telegram
        tg_btn = QPushButton("🤖 Отправить через Telegram")
        tg_btn.clicked.connect(self.send_to_telegram)
        layout.addWidget(tg_btn)

        # Кнопка: Веб-сервис (заглушка)
        web_btn = QPushButton("🌐 Отправить через веб-сервис (скоро)")
        web_btn.setEnabled(False)
        layout.addWidget(web_btn)

        # Кнопка завершения
        done_btn = QPushButton("✅ Готово")
        done_btn.clicked.connect(self.parent.show_main_menu)
        layout.addWidget(done_btn)

        return layout

    def save_to_usb(self):
        # Ищем путь к смонтированной флешке
        base_path = "/media"  # типичное место монтирования
        for root, dirs, _ in os.walk(base_path):
            for d in dirs:
                usb_path = os.path.join(root, d)
                kiosk_dir = os.path.join(usb_path, "KIOSK_SCANS")
                try:
                    os.makedirs(kiosk_dir, exist_ok=True)
                    shutil.copy2(self.file_path, kiosk_dir)
                    QMessageBox.information(self, "✅ Успешно", f"Файл сохранён в: {kiosk_dir}")
                    return
                except Exception as e:
                    continue

        QMessageBox.warning(self, "⚠️ Не найдено", "Флешка не найдена или доступ запрещён.")

    def send_to_telegram(self):
        import uuid
        import json
        import qrcode
        from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox
        from PyQt5.QtGui import QPixmap
        from PyQt5.QtCore import Qt
        import os

        session_id = f"scan_{uuid.uuid4().hex[:8]}"
        abs_file_path = os.path.abspath(self.file_path)
        rel_file_path = os.path.relpath(abs_file_path, os.path.dirname(__file__))

        sessions_file = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "../../../scan_sessions.json"
        ))

        # 🔸 Загрузка или создание файла сессий
        try:
            if os.path.exists(sessions_file):
                with open(sessions_file, "r", encoding="utf-8") as f:
                    sessions = json.load(f)
            else:
                sessions = {}
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить сессии:\n{e}")
            return

        # 🔸 Формируем download_url (на будущее)
        download_url = f"file://{abs_file_path}"

        # 🔸 Запись новой сессии
        sessions[session_id] = {
            "file_path": abs_file_path,
            "rel_path": rel_file_path,
            "download_url": download_url,
            "used": False
        }

        try:
            with open(sessions_file, "w", encoding="utf-8") as f:
                json.dump(sessions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить сессию:\n{e}")
            return

        # 🔸 Генерация и отображение QR-кода
        qr_url = f"https://t.me/sapat_print_bot?start={session_id}"
        qr_img = qrcode.make(qr_url)
        qr_path = os.path.join(os.path.dirname(__file__), "../../../data/tmp_scan_qr.png")
        qr_img.save(qr_path)

        qr_widget = QWidget(self)
        qr_layout = QVBoxLayout()
        qr_widget.setLayout(qr_layout)

        qr_label = QLabel("📱 Отсканируйте QR-код, чтобы получить скан.")
        qr_label.setAlignment(Qt.AlignCenter)
        qr_layout.addWidget(qr_label)

        qr_image = QLabel()
        qr_image.setPixmap(QPixmap(qr_path).scaled(250, 250, Qt.KeepAspectRatio))
        qr_image.setAlignment(Qt.AlignCenter)
        qr_layout.addWidget(qr_image)

        btn_close = QPushButton("✅ Готово")
        btn_close.clicked.connect(lambda: self.parent.show_main_menu())
        qr_layout.addWidget(btn_close)

        self.parent.clear_central_area()
        self.parent.central_layout.addWidget(qr_widget)
