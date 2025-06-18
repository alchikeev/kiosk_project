from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt

class HeaderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
       
        self.setObjectName("HeaderWidget")
        self.setFixedHeight(int(parent.height() * 0.10))  # 10% от высоты

        # 🔹 ВЕРТИКАЛЬНЫЙ layout всей шапки
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 0, 20, 4)
        main_layout.setSpacing(0)

        # 🔹 Заголовок SAPAT 3.0 по центру
        self.label = QLabel("SAPAT 3.0")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.label.setObjectName("HeaderTitle")
        # 🔹 Горизонтальный слой: пустое пространство + кнопки
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 0)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # 🔹 Контейнер с языковыми кнопками
        lang_container = QWidget()
        lang_container.setFixedWidth(int(parent.width() * 0.43))

        lang_layout = QHBoxLayout()
        lang_layout.setContentsMargins(0, 0, 0, 0)
        lang_layout.setSpacing(5)
        lang_layout.setAlignment(Qt.AlignRight)

        self.lang_buttons = []
        for code, text in [("ru", "Русский"), ("ky", "Кыргызча"), ("en", "English")]:
            btn = QPushButton(text)
            btn.setObjectName("langButton")
            btn.setProperty("lang_code", code)
            self.lang_buttons.append(btn)
            lang_layout.addWidget(btn)

        lang_container.setLayout(lang_layout)

        # Добавим spacer + кнопки в нижний слой
        bottom_row.addWidget(spacer)
        bottom_row.addWidget(lang_container)

        # Сборка всех уровней
        main_layout.addWidget(self.label)
        main_layout.addLayout(bottom_row)

        self.setLayout(main_layout)
