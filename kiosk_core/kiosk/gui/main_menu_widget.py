from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QSizePolicy
from PyQt5.QtCore import Qt

class MainMenuWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MainMenuWidget")

        layout = QGridLayout()
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)

        # Кнопки
        self.print_btn = QPushButton("Распечатать документ")
        self.copy_btn = QPushButton("Копировать документ")
        self.scan_btn = QPushButton("Сканировать документ")
        self.help_btn = QPushButton("Задать вопрос")

        # Присваиваем objectName для стилей
        self.print_btn.setObjectName("MenuRed")
        self.copy_btn.setObjectName("MenuBlue")
        self.scan_btn.setObjectName("MenuOrange")
        self.help_btn.setObjectName("MenuPurple")

        for btn in [self.print_btn, self.copy_btn, self.scan_btn, self.help_btn]:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Сетка 2х2
        layout.addWidget(self.print_btn, 0, 0)
        layout.addWidget(self.copy_btn, 0, 1)
        layout.addWidget(self.scan_btn, 1, 0)
        layout.addWidget(self.help_btn, 1, 1)

        self.setLayout(layout)
