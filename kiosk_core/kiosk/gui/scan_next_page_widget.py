from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from kiosk.utils.translate import t

class ScanNextPageWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.page_num = 1
        self.total_pages = 1

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        layout.setContentsMargins(40, 20, 40, 20)
        self.setLayout(layout)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 24px;")
        layout.addWidget(self.label)

        self.scan_button = QPushButton(t("start_scan"))
        self.scan_button.setFixedHeight(50)
        self.scan_button.clicked.connect(self.scan_current_page)
        layout.addWidget(self.scan_button)

    def set_page(self, current, total):
        self.page_num = current
        self.total_pages = total
        self.label.setText(t("scan_page_text").format(current, total))

    def scan_current_page(self):
        self.parent.perform_scan_step(self.page_num, self.total_pages)
