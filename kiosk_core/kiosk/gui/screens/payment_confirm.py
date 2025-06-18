from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from kiosk.utils.translate import t

class PaymentConfirmWidget(QWidget):
    def __init__(self, parent, file_path, selected_pages, price, on_confirm, on_cancel):
        super().__init__(parent)
        self.parent = parent
        self.file_path = file_path
        self.selected_pages = selected_pages
        self.price = price
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)
        self.setLayout(layout)

        # Заголовок
        title = QLabel("Оплата")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        # Сумма
        info = QLabel(f"💳 Сумма к оплате: {self.price} сом")
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("font-size: 18px;")
        layout.addWidget(info)

        # Кнопка "Оплатить"
        button = QPushButton("Оплатить")
        button.setStyleSheet("font-size: 18px; padding: 12px; font-weight: bold;")
        button.clicked.connect(self.handle_payment)
        layout.addWidget(button)

        # Кнопка "Отмена"
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.on_cancel)
        layout.addWidget(cancel_btn)

    def handle_payment(self):
        # Имитация оплаты — сразу подтверждаем
        self.on_confirm(self.selected_pages)
