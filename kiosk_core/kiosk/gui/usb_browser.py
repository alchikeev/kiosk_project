
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel, QMessageBox, QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt

class USBFileBrowser(QWidget):
    def __init__(self, root_path, on_file_selected, on_back_to_main):
        super().__init__()
        self.root_path = root_path
        self.current_path = root_path
        self.on_file_selected = on_file_selected
        self.on_back_to_main = on_back_to_main

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title = QLabel("📁 Распечатать с USB")
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        self.grid_area = QScrollArea()
        self.grid_area.setWidgetResizable(True)
        self.grid_content = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_content.setLayout(self.grid_layout)
        self.grid_area.setWidget(self.grid_content)
        self.layout.addWidget(self.grid_area)

        self.nav_buttons_layout = QVBoxLayout()

        self.back_folder_btn = QPushButton("⬅ Назад")
        self.back_folder_btn.clicked.connect(self.go_back_folder)
        self.nav_buttons_layout.addWidget(self.back_folder_btn)

        self.back_main_btn = QPushButton("Назад в меню")
        self.back_main_btn.clicked.connect(self.on_back_to_main)
        self.nav_buttons_layout.addWidget(self.back_main_btn)

        self.layout.addLayout(self.nav_buttons_layout)

        self.populate_grid()

    def populate_grid(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if not os.path.exists(self.current_path):
            QMessageBox.warning(self, "Ошибка", "Флешка не найдена.")
            return

        items = sorted(os.listdir(self.current_path))
        row = col = 0
        for item in items:
            full_path = os.path.join(self.current_path, item)
            if os.path.isdir(full_path):
                btn = QPushButton(f"📁 {item}")
                btn.clicked.connect(lambda _, p=full_path: self.enter_folder(p))
            else:
                btn = QPushButton(f"📄 {item}")
                btn.clicked.connect(lambda _, p=full_path: self.on_file_selected(p))
            btn.setFixedSize(150, 100)  # ширина, высота в пикселях
            self.grid_layout.addWidget(btn, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

    def enter_folder(self, folder_path):
        self.current_path = folder_path
        self.populate_grid()

    def go_back_folder(self):
        parent = os.path.dirname(self.current_path)
        if os.path.exists(parent) and parent != self.current_path and parent.startswith(self.root_path):
            self.current_path = parent
            self.populate_grid()
