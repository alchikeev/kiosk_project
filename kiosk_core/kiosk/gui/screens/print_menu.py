from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from kiosk.utils.translate import t

class PrintMenuWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 20, 40, 20)
        self.setLayout(layout)

        # 🔙 Навигация
        nav_layout = QHBoxLayout()
        self.btn_back = QPushButton("← " + t("back"))
        self.btn_home = QPushButton("🏠 " + t("home"))
        self.btn_back.clicked.connect(self.parent.show_main_menu)
        self.btn_home.clicked.connect(self.parent.show_main_menu)
        nav_layout.addWidget(self.btn_back)
        nav_layout.addWidget(self.btn_home)
        layout.addLayout(nav_layout)

        # 📄 Кнопки источников печати
        self.source_buttons = []
        sources = [
            ("from_usb", self.parent.show_usb_documents),
            ("from_telegram", self.parent.show_telegram_print),  # ← вот тут
            ("from_library", self.parent.show_library_browser),
            ("from_web", lambda: self.parent.start_payment_flow("print:web")),
        ]

        for key, handler in sources:
            btn = QPushButton(t(key))
            btn.setObjectName("MenuBlue")
            btn.setFixedHeight(60)
            btn.clicked.connect(handler)
            self.source_buttons.append(btn)
            layout.addWidget(btn)

    def retranslate_ui(self):
        self.btn_back.setText("← " + t("back"))
        self.btn_home.setText("🏠 " + t("home"))

        keys = ["from_usb", "from_telegram", "from_library", "from_web"]
        for i, key in enumerate(keys):
            self.source_buttons[i].setText(t(key))
