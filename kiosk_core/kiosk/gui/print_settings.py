import json
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt

class PrintSettingsWidget(QWidget):
    def __init__(self, total_pages, on_apply, on_cancel):
        super().__init__()
        self.total_pages = total_pages
        self.on_apply = on_apply
        self.on_cancel = on_cancel

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(30, 10, 30, 10)
        self.layout.setSpacing(15)
        self.setLayout(self.layout)

        # Заголовок
        title = QLabel("Подтверждение печати")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.layout.addWidget(title)

        # Навигация
        nav = QHBoxLayout()
        back = QPushButton("← Назад")
        home = QPushButton("🏠 Главная")
        back.clicked.connect(self.on_cancel)
        home.clicked.connect(self.on_cancel)
        for btn in (back, home):
            btn.setStyleSheet("font-size: 16px; padding: 6px 12px;")
            nav.addWidget(btn)
        self.layout.addLayout(nav)

        # Превью
        preview = QLabel("🖼️ Превью документа (заглушка)")
        preview.setAlignment(Qt.AlignCenter)
        preview.setStyleSheet("border: 1px solid #ccc; padding: 20px; font-size: 16px;")
        self.layout.addWidget(preview)

        # Информация
        self.pages_label = QLabel(f"Всего страниц: {self.total_pages}")
        self.pages_label.setStyleSheet("font-size: 16px;")
        self.layout.addWidget(self.pages_label)

        # Цена за страницу
        try:
            with open(os.path.join(os.path.dirname(__file__), '../../settings.json'), 'r', encoding='utf-8') as f:
                settings = json.load(f)
            self.price_per_page = settings.get("price_per_page", 10)
        except:
            self.price_per_page = 10

        self.cost_label = QLabel()
        self.cost_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout.addWidget(self.cost_label)

        # Диапазон ввода
        self.range_label = QLabel("Введите диапазон страниц (например: 1-5,8,10):")
        self.range_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.range_label)

        self.range_input = QLineEdit()
        self.range_input.setStyleSheet("font-size: 16px; padding: 6px;")
        self.range_input.textChanged.connect(self.update_price_preview)
        self.layout.addWidget(self.range_input)

        # Кнопки действия
        btns = QHBoxLayout()
        self.confirm_btn = QPushButton("Далее")
        self.confirm_btn.setStyleSheet("font-size: 18px; padding: 10px; font-weight: bold;")
        self.confirm_btn.clicked.connect(self.handle_apply)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet("font-size: 16px; padding: 8px;")
        cancel_btn.clicked.connect(self.on_cancel)
        btns.addWidget(self.confirm_btn)
        btns.addWidget(cancel_btn)
        self.layout.addLayout(btns)

        self.update_price_preview()

    def parse_page_range(self, text):
        pages = set()
        parts = text.split(',')
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    if start <= end:
                        pages.update(range(start, end + 1))
                except:
                    continue
            else:
                try:
                    pages.add(int(part))
                except:
                    continue
        return sorted(p for p in pages if 1 <= p <= self.total_pages)

    def update_price_preview(self):
        text = self.range_input.text().strip()
        if not text:
            pages_count = self.total_pages
        else:
            try:
                selected_pages = self.parse_page_range(text)
                pages_count = len(selected_pages)
            except:
                pages_count = 0
        total_price = pages_count * self.price_per_page
        self.cost_label.setText(f"Стоимость: {total_price} сом")

    def handle_apply(self):
        text = self.range_input.text().strip()
        if not text:
            selected_pages = list(range(1, self.total_pages + 1))
        else:
            try:
                selected_pages = self.parse_page_range(text)
                if not selected_pages:
                    raise ValueError
            except:
                QMessageBox.critical(self, "Ошибка", "Неверный формат диапазона.")
                return
        self.on_apply(selected_pages)
