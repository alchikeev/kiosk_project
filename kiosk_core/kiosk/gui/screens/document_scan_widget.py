from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
import os
from datetime import datetime
from PIL import Image

from kiosk.utils.translate import t

class DocumentScanWidget(QWidget):
    def __init__(self, parent, total_pages):
        super().__init__(parent)
        self.parent = parent
        self.total_pages = total_pages
        self.scanned_pages = 0
        self.scanned_files = []

        self.setLayout(self.build_ui())

    def build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        # 🔝 Навигация
        nav_layout = QHBoxLayout()
        btn_back = QPushButton("← " + t("back"))
        btn_back.clicked.connect(self.parent.show_main_menu)
        title = QLabel(t("scan_document"))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        nav_layout.addWidget(btn_back)
        nav_layout.addWidget(title)
        nav_layout.addStretch()
        layout.addLayout(nav_layout)

        # 📄 Счётчик
        self.counter_label = QLabel()
        self.counter_label.setAlignment(Qt.AlignCenter)
        self.counter_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(self.counter_label)
        self.update_counter()

        # 🔘 Кнопки
        self.scan_btn = QPushButton("📄 " + t("scan_next_page"))
        self.scan_btn.clicked.connect(self.scan_next_page)
        layout.addWidget(self.scan_btn)

        self.done_btn = QPushButton("⏭ " + t("next"))
        self.done_btn.clicked.connect(self.finish_scanning)
        layout.addWidget(self.done_btn)

        return layout

    def update_counter(self):
        left = self.total_pages - self.scanned_pages
        self.counter_label.setText(f"Сканировано: {self.scanned_pages} / {self.total_pages} — Осталось: {left}")

    def scan_next_page(self):
        filename = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        output_dir = os.path.join("data", "scans")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)

        try:
            import subprocess
            subprocess.run([
                "scanimage",
                "--format=png",
                f"--output-file={output_path}"
            ], check=True)
            self.scanned_files.append(output_path)
            self.scanned_pages += 1
            self.update_counter()

            if self.scanned_pages >= self.total_pages:
                self.finish_scanning()

        except Exception as e:
            self.parent.show_message("Ошибка сканирования", str(e), error=True)

    def finish_scanning(self):
        if not self.scanned_files:
            self.parent.show_message("Нет сканов", "Вы не отсканировали ни одной страницы.", error=True)
            return

        pdf_path = os.path.join("data", "scans", f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        try:
            images = [Image.open(f).convert("RGB") for f in self.scanned_files]
            images[0].save(pdf_path, save_all=True, append_images=images[1:])
        except Exception as e:
            self.parent.show_message("Ошибка PDF", f"Не удалось сохранить PDF: {e}", error=True)
            return

        # Очистка PNG после сборки
        for f in self.scanned_files:
            try:
                os.remove(f)
            except:
                pass

        # Переход к экрану отправки
        self.parent.show_send_options(pdf_path)