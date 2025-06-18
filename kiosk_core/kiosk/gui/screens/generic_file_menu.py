from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from kiosk.utils.translate import t
from kiosk.io.doc_utils import count_pages
from kiosk.gui.print_settings import PrintSettingsWidget
from config import SETTINGS
from kiosk.gui.screens.payment_confirm import PaymentConfirmWidget


class GenericFileMenuWidget(QWidget):
    def __init__(self, parent, title, root_path, file_browser_class, back_callback):
        super().__init__(parent)
        self.parent = parent
        self.root_path = root_path
        self.back_callback = back_callback
        self.SETTINGS = SETTINGS

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        # Навигация
        nav_layout = QHBoxLayout()
        btn_back = QPushButton("← " + t("back"))
        btn_home = QPushButton("🏠 " + t("home"))
        btn_back.clicked.connect(self.back_callback)
        btn_home.clicked.connect(self.parent.show_main_menu)
        nav_layout.addWidget(btn_back)
        nav_layout.addWidget(btn_home)
        layout.addLayout(nav_layout)

        # Заголовок
        from PyQt5.QtWidgets import QLabel
        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Файловый браузер
        self.browser = file_browser_class(
            root_path=root_path,
            on_file_selected=self.on_file_selected,
            on_back_to_main=self.back_callback
        )
        layout.addWidget(self.browser)

    def on_file_selected(self, file_path):
        try:
            pages = count_pages(file_path)
            price_per_page = self.SETTINGS.get("price_per_page", 5)
            full_price = pages * price_per_page
        except Exception as e:
            self.parent.show_message("Ошибка", f"Не удалось определить цену:\\n{str(e)}", error=True)
            return

        def next_step(selected_pages):
            price = len(selected_pages) * price_per_page
            def confirm_and_print(_pages):
                from kiosk.io.printer import print_file
                print_file(file_path, pages=_pages)
                self.parent.show_message("✅ Успешно", "Файл отправлен на печать.")
                self.parent.show_main_menu()

            self.parent.clear_central_area()
            self.parent.central_layout.addWidget(PaymentConfirmWidget(
                parent=self.parent,
                file_path=file_path,
                selected_pages=selected_pages,
                price=price,
                on_confirm=confirm_and_print,
                on_cancel=self.parent.show_main_menu
            ))

        self.parent.clear_central_area()
        self.parent.central_layout.addWidget(PrintSettingsWidget(
            total_pages=pages,
            on_apply=next_step,
            on_cancel=self.parent.show_main_menu
        ))
