import sys
import os
import uuid
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt

from kiosk.utils.translate import t, set_language
from kiosk.core.logger import init_db, log_event, get_device_id
from kiosk.session import SessionState
from kiosk.io.printer import print_file
from kiosk.gui.header_widget import HeaderWidget
from kiosk.gui.main_menu_widget import MainMenuWidget
from kiosk.gui.screens.print_menu import PrintMenuWidget
from kiosk.gui.copy_settings import CopySettingsWidget
from kiosk.gui.scan_next_page_widget import ScanNextPageWidget
from kiosk.gui.library_browser import LibraryFileBrowser
from kiosk.gui.screens.generic_file_menu import GenericFileMenuWidget
from kiosk.gui.usb_browser import USBFileBrowser
from kiosk.gui.library_browser import LibraryFileBrowser
from kiosk.io.usb import get_usb_mount_path
from config import SETTINGS
from kiosk.gui.screens.payment_confirm import PaymentConfirmWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.session = SessionState()
        self.setWindowTitle(t("window_title"))
        self.resize(540, 960)
        self.device_id = get_device_id()
        self.session_id = str(uuid.uuid4())
        init_db()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 🔝 Header
        self.header_widget = HeaderWidget(self)
        self.layout.addWidget(self.header_widget)
        for btn in self.header_widget.lang_buttons:
            code = btn.property("lang_code")
            btn.clicked.connect(self._make_lang_handler(code))

        # 🧩 Central area
        self.central_area = QWidget()
        self.central_layout = QVBoxLayout()
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_area.setLayout(self.central_layout)
        self.layout.addWidget(self.central_area, stretch=1)

        self.main_menu = MainMenuWidget(self)
        self.central_layout.addWidget(self.main_menu)
        self.main_menu.print_btn.clicked.connect(self.show_print_menu)
        self.main_menu.copy_btn.clicked.connect(self.show_copy_menu)
        self.main_menu.scan_btn.clicked.connect(self.show_scan_menu)
        self.main_menu.help_btn.clicked.connect(self.show_help_menu)
        self.copy_settings_widget = CopySettingsWidget(self)
        self.scan_widget = ScanNextPageWidget(self)
        # 🔻 Footer
        self.footer = QWidget()
        self.footer_layout = QHBoxLayout()
        self.footer.setLayout(self.footer_layout)
        self.layout.addWidget(self.footer)

        self.price_btn = QPushButton(t("price_list"))
        self.partner_btn = QPushButton(t("become_partner"))
        self.footer_layout.addWidget(self.price_btn)
        self.footer_layout.addWidget(self.partner_btn)

        self.price_btn.clicked.connect(lambda: QMessageBox.information(self, t("info"), t("price_list_info")))
        self.partner_btn.clicked.connect(lambda: QMessageBox.information(self, t("info"), t("become_partner_info")))

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_session)
        self.timer.start(1000)

    def _make_lang_handler(self, code):
        return lambda _: self.change_language(code)

    def change_language(self, lang_code):
        set_language(lang_code)
        self.session.language = lang_code
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(t("window_title"))
        for btn in self.header_widget.lang_buttons:
            lang_code = btn.property("lang_code")
            if lang_code == "ru":
                btn.setText(t("Русский"))
            elif lang_code == "ky":
                btn.setText(t("Кыргызча"))
            elif lang_code == "en":
                btn.setText(t("English"))
            if self.central_layout.count() > 0:
                widget = self.central_layout.itemAt(0).widget()
                if hasattr(widget, "retranslate_ui"):
                    widget.retranslate_ui()


        self.main_menu.print_btn.setText(t("print_document"))
        self.main_menu.copy_btn.setText(t("copy_document"))
        self.main_menu.scan_btn.setText(t("scan_document"))
        self.main_menu.help_btn.setText(t("ask_question"))
        self.price_btn.setText(t("price_list"))
        self.partner_btn.setText(t("become_partner"))

    def clear_central_area(self):
        for i in reversed(range(self.central_layout.count())):
            widget = self.central_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def show_main_menu(self):
        self.clear_central_area()
        self.central_layout.addWidget(self.main_menu)

    def show_print_menu(self):
        self.clear_central_area()
        self.central_layout.addWidget(PrintMenuWidget(self))

    def show_library_browser(self):
        self.clear_central_area()
        self.central_layout.addWidget(GenericFileMenuWidget(
            parent=self,
            title="📚 Печать из библиотеки",
            root_path="data/library_docs",
            file_browser_class=LibraryFileBrowser,
            back_callback=self.show_print_menu
        ))


    def show_copy_menu(self):
        self.clear_central_area()
        self.central_layout.addWidget(self.copy_settings_widget)

    def start_copy_payment(self, pages_count):
        from kiosk.gui.screens.payment_confirm import PaymentConfirmWidget
        from config import SETTINGS

        self.copy_pages_count = pages_count
        price_per_page = SETTINGS.get("copy_price_per_page", 10)
        total_price = pages_count * price_per_page

        def confirm_and_start_copy(_):
            self.copy_pages_remaining = pages_count
            self.copy_total_price = total_price
            self.show_message(t("payment_success"), t("payment_done"))
            self.show_scan_step(1, pages_count)

        self.clear_central_area()
        self.central_layout.addWidget(PaymentConfirmWidget(
            parent=self,
            file_path="copy_job",  # фиктивное имя, не используется
            selected_pages=list(range(1, pages_count + 1)),  # условно
            price=total_price,
            on_confirm=confirm_and_start_copy,
            on_cancel=self.show_main_menu
        ))

    def show_scan_step(self, current, total):
        self.scan_widget.set_page(current, total)
        self.clear_central_area()
        self.central_layout.addWidget(self.scan_widget)

    def perform_scan_step(self, current, total):
        from kiosk.io.scanner import scan_document
        from kiosk.io.printer import print_file
        import os

        output_file = scan_document(f"copy_page_{current}")
        if output_file:
            print_file(output_file)
            try:
                os.remove(output_file)
                print(f"🗑 Удалён скан: {output_file}")
            except Exception as e:
                print(f"⚠️ Ошибка при удалении: {e}")

            if current < total:
                QTimer.singleShot(1000, lambda: self.show_scan_step(current + 1, total))
            else:
                self.show_message(t("copy_complete"), t("all_pages_copied"))
                self.show_main_menu()
        else:
            self.show_message(t("scan_failed"), t("try_again"), error=True)


    def show_scan_menu(self):
        from kiosk.gui.copy_settings import CopySettingsWidget
        self.clear_central_area()
        self.central_layout.addWidget(CopySettingsWidget(self, for_scan=True))

    def show_help_menu(self):
        QMessageBox.information(self, t("faq"), t("help_info"))

    def check_session(self):
        if self.session.status == "waiting" and self.session.is_expired():
            session.status = "expired"
            log_event(self.operation_code, self.session.operation, 0, "waiting", "timeout")
            QMessageBox.warning(self, t("session_expired_title"), t("session_expired"))
            self.show_main_menu()

    def __del__(self):
        if hasattr(self, "operation_code"):
            log_event(self.operation_code, session.operation, 0, session.status, "completed")
    
    def show_usb_documents(self):
        mounts = get_usb_mount_path()
        if not mounts:
            self.show_message("Ошибка", "Флешка не найдена", error=True)
            return

        usb_path = mounts[0]  # берём первую доступную флешку
        self.clear_central_area()
        self.central_layout.addWidget(GenericFileMenuWidget(
            parent=self,
            title="📁 Печать с USB",
            root_path=usb_path,
            file_browser_class=USBFileBrowser,
            back_callback=self.show_print_menu
        ))



        
    def start_scan_payment(self, pages_count):
        from kiosk.gui.screens.payment_confirm import PaymentConfirmWidget
        from config import SETTINGS

        price_per_page = SETTINGS.get("scan_price_per_page", 8)
        total_price = pages_count * price_per_page

        def confirm_and_start_scan(_):
            self.scan_pages_remaining = pages_count
            self.show_document_scan_step(1, pages_count)

        self.clear_central_area()
        self.central_layout.addWidget(PaymentConfirmWidget(
            parent=self,
            file_path="scan_job",
            selected_pages=list(range(1, pages_count + 1)),
            price=total_price,
            on_confirm=confirm_and_start_scan,
            on_cancel=self.show_main_menu
        ))

    def show_document_scan_step(self, current, total):
        from kiosk.gui.screens.document_scan_widget import DocumentScanWidget
        self.clear_central_area()
        self.central_layout.addWidget(DocumentScanWidget(self, total_pages=total))

    def show_send_options(self, file_path):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Сканирование завершено", f"Файл сохранён:\n{file_path}\n\nПока доступна только отправка на USB.")
        self.show_main_menu()

    def show_send_options(self, file_path):
        from kiosk.gui.screens.send_scanned_file_widget import SendScannedFileWidget
        self.clear_central_area()
        self.central_layout.addWidget(SendScannedFileWidget(self, file_path))


    def get_timestamp(self):
        return time.time()

    def show_message(self, title, text, error=False):
        from PyQt5.QtWidgets import QMessageBox
        if error:
            QMessageBox.critical(self, title, text)
        else:
            QMessageBox.information(self, title, text)
    
    def show_telegram_print(self):
        from kiosk.gui.screens.print_from_telegram_widget import PrintFromTelegramWidget
        self.clear_central_area()
        self.central_layout.addWidget(PrintFromTelegramWidget(self))

    def show_page_selection_for_telegram(self, file_path):
        from kiosk.io.doc_utils import count_pages
        from kiosk.gui.print_settings import PrintSettingsWidget

        try:
            total_pages = count_pages(file_path)
        except Exception as e:
            self.show_message("Ошибка", f"Не удалось определить количество страниц:\n{e}", error=True)
            return

        def on_apply(selected_pages):
            from kiosk.gui.screens.payment_confirm import PaymentConfirmWidget

            price_per_page = SETTINGS.get("print_price_per_page", 5)
            price = price_per_page * len(selected_pages)

            def confirm_and_print(_):
                print_file(file_path, pages=selected_pages)
                self.show_message("Успех", "Файл отправлен на печать.")
                self.show_main_menu()

            self.clear_central_area()
            self.central_layout.addWidget(PaymentConfirmWidget(
                parent=self,
                file_path=file_path,
                selected_pages=selected_pages,
                price=price,
                on_confirm=confirm_and_print,
                on_cancel=self.show_main_menu
            ))

        def on_cancel():
            self.show_main_menu()

        self.clear_central_area()
        self.central_layout.addWidget(PrintSettingsWidget(
            total_pages=total_pages,
            on_apply=on_apply,
            on_cancel=on_cancel
        ))

def start_gui():
    app = QApplication(sys.argv)
    style_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "style.qss")
    if os.path.exists(style_file_path):
        with open(style_file_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    start_gui()
