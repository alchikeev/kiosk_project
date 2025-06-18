from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpinBox, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from kiosk.utils.translate import t
from config import MAX_PAGES

class CopySettingsWidget(QWidget):
    def __init__(self, parent, for_scan=False):
        super().__init__(parent)
        self.parent = parent
        self.for_scan = for_scan

        # Основной вертикальный лэйаут
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 20, 40, 20)
        self.setLayout(layout)

        # 🔝 Навигационная панель
        nav_layout = QHBoxLayout()
        btn_back = QPushButton("← " + t("back"))
        btn_back.clicked.connect(self.parent.show_main_menu)

        # Заголовок в зависимости от режима
        title_label = QLabel(t("scan_document") if self.for_scan else t("copy_document"))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        nav_layout.addWidget(btn_back)
        nav_layout.addWidget(title_label)
        nav_layout.addStretch()
        layout.addLayout(nav_layout)

        # Вопрос
        label = QLabel(t("how_many_pages"))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 24px;")
        layout.addWidget(label)

        # Поле ввода количества страниц
        self.page_spinbox = QSpinBox()
        self.page_spinbox.setMinimum(1)
        self.page_spinbox.setMaximum(MAX_PAGES)
        self.page_spinbox.setValue(1)
        layout.addWidget(self.page_spinbox)

        # Кнопка "Продолжить"
        btn_continue = QPushButton(t("continue"))
        btn_continue.setStyleSheet("font-size: 18px; padding: 10px;")
        btn_continue.clicked.connect(self.continue_to_payment)
        layout.addWidget(btn_continue)

    def continue_to_payment(self):
        count = self.page_spinbox.value()

        if count > MAX_PAGES:
            QMessageBox.warning(self, t("limit"), f"{t('max')} {MAX_PAGES}")
            return

        if self.for_scan:
            self.parent.start_scan_payment(count)
        else:
            self.parent.start_copy_payment(count)
