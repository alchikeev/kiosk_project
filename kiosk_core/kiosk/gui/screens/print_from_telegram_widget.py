import os
import time
import qrcode
import threading
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer

QR_PATH = "data/tmp_qr.png"
WATCH_FOLDER = "data/remote_files"

class PrintFromTelegramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = self.find_main_window()
        self._last_received_path = None

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        self.label = QLabel("Отсканируйте QR-код, чтобы отправить файл в Telegram-боте")
        layout.addWidget(self.label)

        self.qr = QLabel()
        layout.addWidget(self.qr)

        self.generate_qr("session_kiosk007_xyz")
        self.watch_for_file()
    
    def find_main_window(self):
        from kiosk.gui.main import MainWindow
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, MainWindow):
                return parent
            parent = parent.parent()
        raise RuntimeError("MainWindow не найден как родитель")

    def generate_qr(self, session_id):
        url = f"https://t.me/sapat_print_bot?start={session_id}"
        img = qrcode.make(url)
        img.save(QR_PATH)
        self.qr.setPixmap(QPixmap(QR_PATH).scaled(200, 200, Qt.KeepAspectRatio))

    def watch_for_file(self):
        self._start_time = time.time()

        def check_loop():
            while True:
                try:
                    for fname in os.listdir(WATCH_FOLDER):
                        if not fname.lower().endswith((".pdf", ".docx")):
                            continue
                        path = os.path.join(WATCH_FOLDER, fname)
                        created_at = os.path.getctime(path)
                        if created_at < self._start_time:
                            continue  # файл старый, игнорируем

                        print(f"📥 Получен новый файл: {path}")
                        self._last_received_path = path
                        QTimer.singleShot(0, self.on_file_received)
                        return
                except Exception as e:
                    print(f"Ошибка при мониторинге файлов: {e}")
                time.sleep(2)

        import threading
        threading.Thread(target=check_loop, daemon=True).start()

    def on_file_received(self):
        print("📤 Переход к выбору страниц из Telegram...")
        self.main_window.show_page_selection_for_telegram(self._last_received_path)

