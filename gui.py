"""
GUI — PyQt6 интерфейс
"""

import os
import logging
import threading
from about import get_about_text, APP_NAME, APP_VERSION
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox,
    QCheckBox, QProgressBar, QGroupBox, QFileDialog,
    QMessageBox, QMenu, QApplication, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QShortcut, QKeySequence

from config import AppConfig
from translations import TRANSLATIONS, get_text
from network import URLValidator
from parser import GuideDownloader
from utils import validate_save_path
from themes import load_theme, get_available_themes

logger = logging.getLogger(__name__)


class LogSignal(QObject):
    """Потокобезопасный сигнал для логирования"""
    message = pyqtSignal(str)
    finished = pyqtSignal()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = AppConfig.load()
        self.downloader = None
        self.log_signal = LogSignal()
        self.log_signal.message.connect(self._append_log)
        self.log_signal.finished.connect(self._on_download_finished)

        self._setup_ui()
        self._update_texts()
        self._apply_theme(self.config.theme)
        self._setup_paste_shortcuts()

    # ==========================================
    # PASTE SHORTCUTS (все раскладки)
    # ==========================================

    def _setup_paste_shortcuts(self):
        shortcut_v = QShortcut(QKeySequence("Ctrl+V"), self)
        shortcut_v.activated.connect(self._paste_to_focused)

        shortcut_ru = QShortcut(QKeySequence("Ctrl+М"), self)
        shortcut_ru.activated.connect(self._paste_to_focused)

        shortcut_ins = QShortcut(QKeySequence("Shift+Insert"), self)
        shortcut_ins.activated.connect(self._paste_to_focused)

    def _paste_to_focused(self):
        focused = QApplication.focusWidget()
        if isinstance(focused, QLineEdit):
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            if text:
                focused.insert(text.strip())

    # ==========================================
    # UI SETUP
    # ==========================================

    def _setup_ui(self):
        self.setMinimumSize(750, 700)
        self.resize(800, 700)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(8)

        # --- Заголовок ---
        self.title_label = QLabel()
        self.title_label.setObjectName("title_label")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("subtitle_label")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.subtitle_label)

        # --- URL Group ---
        url_group = QGroupBox()
        self.url_group = url_group
        url_layout = QVBoxLayout(url_group)

        self.lbl_url = QLabel()
        url_layout.addWidget(self.lbl_url)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "https://steamcommunity.com/sharedfiles/filedetails/?id=..."
        )
        self.url_input.setClearButtonEnabled(True)
        self.url_input.returnPressed.connect(self.start_download)
        self.url_input.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.url_input.customContextMenuRequested.connect(
            self._url_context_menu
        )
        url_layout.addWidget(self.url_input)
        layout.addWidget(url_group)

        # --- Save Path Group ---
        path_group = QGroupBox()
        self.path_group = path_group
        path_layout = QVBoxLayout(path_group)

        self.lbl_path = QLabel()
        path_layout.addWidget(self.lbl_path)

        path_row = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setText(self.config.save_dir)
        self.path_input.setPlaceholderText("/path/to/save/folder")
        self.path_input.editingFinished.connect(self._on_path_edited)
        self.path_input.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.path_input.customContextMenuRequested.connect(
            self._path_context_menu
        )

        self.btn_browse = QPushButton()
        self.btn_browse.setFixedWidth(100)
        self.btn_browse.clicked.connect(self._browse_folder)

        path_row.addWidget(self.path_input)
        path_row.addWidget(self.btn_browse)
        path_layout.addLayout(path_row)

        self.path_error_label = QLabel("")
        self.path_error_label.setStyleSheet("color: #ff4444; font-size: 8pt;")
        self.path_error_label.setVisible(False)
        path_layout.addWidget(self.path_error_label)

        layout.addWidget(path_group)

        # --- Options Row ---
        options_layout = QHBoxLayout()

        self.chk_pdf = QCheckBox()
        self.chk_pdf.setChecked(self.config.convert_to_pdf)
        self.chk_pdf.toggled.connect(self._on_pdf_toggled)
        options_layout.addWidget(self.chk_pdf)

        self.pdf_status_label = QLabel("")
        self.pdf_status_label.setStyleSheet("font-size: 8pt;")
        options_layout.addWidget(self.pdf_status_label)

        options_layout.addStretch()

        self.lbl_theme = QLabel()
        options_layout.addWidget(self.lbl_theme)

        self.combo_theme = QComboBox()
        themes = get_available_themes()
        self.combo_theme.addItems([t.capitalize() for t in themes])
        self._theme_names = themes
        if self.config.theme in themes:
            self.combo_theme.setCurrentIndex(themes.index(self.config.theme))
        self.combo_theme.currentIndexChanged.connect(self._on_theme_changed)
        options_layout.addWidget(self.combo_theme)

        self.lbl_lang = QLabel()
        options_layout.addWidget(self.lbl_lang)

        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["English", "Русский"])
        self.combo_lang.setCurrentIndex(
            0 if self.config.language == "en" else 1
        )
        self.combo_lang.currentIndexChanged.connect(self._on_lang_changed)
        options_layout.addWidget(self.combo_lang)

        layout.addLayout(options_layout)

        # --- Buttons ---
        btn_layout = QHBoxLayout()

        self.btn_download = QPushButton()
        self.btn_download.setObjectName("btn_download")
        self.btn_download.clicked.connect(self.start_download)
        self.btn_download.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        self.btn_cancel = QPushButton()
        self.btn_cancel.setObjectName("btn_cancel")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel_download)
        self.btn_cancel.setFixedWidth(120)

        btn_layout.addWidget(self.btn_download)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        # --- Progress ---
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # --- Log ---
        log_header = QHBoxLayout()
        self.lbl_log = QLabel()
        log_header.addWidget(self.lbl_log)
        log_header.addStretch()

        self.btn_clear_log = QPushButton()
        self.btn_clear_log.setFixedHeight(28)
        self.btn_clear_log.clicked.connect(self._clear_log)
        log_header.addWidget(self.btn_clear_log)

        layout.addLayout(log_header)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.log_area.customContextMenuRequested.connect(
            self._log_context_menu
        )
        layout.addWidget(self.log_area, stretch=1)
        
        self._create_menu_bar()
        # Проверяем PDF
        self._check_pdf_availability()
    
    def _create_menu_bar(self):
        """Создание главного меню"""
        menubar = self.menuBar()

        # Файл
        self.file_menu = menubar.addMenu("")
        self.exit_action = self.file_menu.addAction("")
        self.exit_action.triggered.connect(self.close)

        # Справка
        self.help_menu = menubar.addMenu("")
        self.about_action = self.help_menu.addAction("")
        self.about_action.triggered.connect(self._show_about)

    def _show_about(self):
        """Окно 'О программе'"""
        about_text = get_about_text(self.config.language)
        QMessageBox.about(self, f"About {APP_NAME}", about_text)
    
    # ==========================================
    # PDF CHECK
    # ==========================================

    def _check_pdf_availability(self):
        from pdf_converter import check_available_converters
        converters = check_available_converters()
        available = [name for name, ok in converters.items() if ok]

        if available:
            names = ", ".join(available)
            self.pdf_status_label.setText(f"✅ {names}")
            self.pdf_status_label.setStyleSheet(
                "font-size: 8pt; color: #44aa44;"
            )
            self.chk_pdf.setEnabled(True)
        else:
            self.pdf_status_label.setText("❌ No converter")
            self.pdf_status_label.setStyleSheet(
                "font-size: 8pt; color: #aa4444;"
            )
            self.chk_pdf.setEnabled(False)
            self.chk_pdf.setChecked(False)
            self.chk_pdf.setToolTip(
                "Install pywin32, docx2pdf, or LibreOffice"
            )

    # ==========================================
    # CONTEXT MENUS
    # ==========================================

    def _url_context_menu(self, pos):
        lang = self.config.language
        menu = QMenu(self)
        paste_act = menu.addAction(get_text(lang, "ctx_paste"))
        paste_act.triggered.connect(
            lambda: self._paste_to_widget(self.url_input)
        )
        clear_act = menu.addAction("Clear")
        clear_act.triggered.connect(self.url_input.clear)
        menu.exec(self.url_input.mapToGlobal(pos))

    def _path_context_menu(self, pos):
        menu = QMenu(self)
        paste_act = menu.addAction("Paste")
        paste_act.triggered.connect(
            lambda: self._paste_to_widget(self.path_input)
        )
        clear_act = menu.addAction("Clear")
        clear_act.triggered.connect(self.path_input.clear)
        menu.exec(self.path_input.mapToGlobal(pos))

    def _log_context_menu(self, pos):
        lang = self.config.language
        menu = QMenu(self)
        copy_act = menu.addAction(get_text(lang, "ctx_copy_all"))
        copy_act.triggered.connect(self._copy_log)
        menu.addSeparator()
        clear_act = menu.addAction(get_text(lang, "btn_clear_log"))
        clear_act.triggered.connect(self._clear_log)
        menu.exec(self.log_area.mapToGlobal(pos))

    def _paste_to_widget(self, widget: QLineEdit):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            widget.clear()
            widget.insert(text.strip())

    def _copy_log(self):
        text = self.log_area.toPlainText().strip()
        if text:
            QApplication.clipboard().setText(text)

    # ==========================================
    # TEXT UPDATES
    # ==========================================

    def _update_texts(self):
        lang = self.config.language
        T = lambda key: get_text(lang, key)

        self.setWindowTitle(T("window_title"))
        self.title_label.setText(T("window_title"))
        self.subtitle_label.setText(T("app_subtitle"))
        self.url_group.setTitle(T("lbl_url"))
        self.lbl_url.setText(T("lbl_url"))
        self.path_group.setTitle(T("lbl_path"))
        self.lbl_path.setText(T("lbl_path"))
        self.btn_browse.setText(T("btn_browse"))
        self.btn_download.setText(T("btn_download"))
        self.btn_cancel.setText(T("btn_cancel"))
        self.chk_pdf.setText(T("chk_pdf"))
        self.lbl_theme.setText(T("lbl_theme"))
        self.lbl_lang.setText(T("lbl_lang"))
        self.lbl_log.setText(T("lbl_log"))
        self.btn_clear_log.setText(T("btn_clear_log"))
        if hasattr(self, 'file_menu'):
            self.file_menu.setTitle(T("menu_file"))
            self.exit_action.setText(T("menu_exit"))
            self.help_menu.setTitle(T("menu_help"))
            self.about_action.setText(T("menu_about"))

    # ==========================================
    # THEME / LANG / OPTIONS
    # ==========================================

    def _apply_theme(self, theme_name: str):
        qss = load_theme(theme_name)
        self.setStyleSheet(qss)

    def _on_theme_changed(self, index: int):
        if 0 <= index < len(self._theme_names):
            theme = self._theme_names[index]
            self.config.theme = theme
            self.config.save()
            self._apply_theme(theme)

    def _on_lang_changed(self, index: int):
        lang = "en" if index == 0 else "ru"
        self.config.language = lang
        self.config.save()
        self._update_texts()

    def _on_pdf_toggled(self, checked: bool):
        self.config.convert_to_pdf = checked
        self.config.save()

    # ==========================================
    # PATH VALIDATION
    # ==========================================

    def _browse_folder(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Folder", self.config.save_dir
        )
        if directory:
            self.path_input.setText(directory)
            self.config.save_dir = directory
            self.config.save()
            self.path_error_label.setVisible(False)
            self.path_input.setStyleSheet("")

    def _on_path_edited(self):
        path = self.path_input.text().strip()
        if not path:
            return
        is_valid, result = validate_save_path(path)
        if is_valid:
            self.config.save_dir = result
            self.path_input.setText(result)
            self.config.save()
            self.path_error_label.setVisible(False)
            self.path_input.setStyleSheet("")
        else:
            self.path_error_label.setText(f"⚠ {result}")
            self.path_error_label.setVisible(True)
            self.path_input.setStyleSheet("border-color: #ff4444;")

    def _validate_path_before_download(self) -> bool:
        path = self.path_input.text().strip()
        lang = self.config.language
        if not path:
            QMessageBox.warning(
                self,
                get_text(lang, "msg_validation_title"),
                get_text(lang, "err_bad_path")
            )
            return False
        is_valid, result = validate_save_path(path)
        if not is_valid:
            QMessageBox.warning(
                self,
                get_text(lang, "msg_validation_title"),
                f"{get_text(lang, 'err_bad_path')}\n\n{result}"
            )
            self.path_error_label.setText(f"⚠ {result}")
            self.path_error_label.setVisible(True)
            self.path_input.setStyleSheet("border-color: #ff4444;")
            return False
        self.config.save_dir = result
        self.path_input.setText(result)
        self.config.save()
        self.path_error_label.setVisible(False)
        self.path_input.setStyleSheet("")
        return True

    # ==========================================
    # LOG
    # ==========================================

    def _append_log(self, message: str):
        self.log_area.append(message)

    def _clear_log(self):
        self.log_area.clear()

    def _log_threadsafe(self, message: str):
        self.log_signal.message.emit(message)

    # ==========================================
    # DOWNLOAD
    # ==========================================

    def start_download(self):
        url = self.url_input.text().strip()
        lang = self.config.language

        if not url:
            QMessageBox.warning(
                self,
                get_text(lang, "msg_warning"),
                get_text(lang, "err_no_url")
            )
            self.url_input.setFocus()
            return

        is_valid, result = URLValidator.validate(url)
        if not is_valid:
            QMessageBox.warning(
                self,
                get_text(lang, "msg_validation_title"),
                f"{get_text(lang, 'err_bad_url')}\n\n({result})"
            )
            self.url_input.setFocus()
            self.url_input.selectAll()
            return

        if not self._validate_path_before_download():
            return

        normalized_url = result

        self.btn_download.setEnabled(False)
        self.btn_download.setText(get_text(lang, "btn_downloading"))
        self.btn_cancel.setEnabled(True)
        self.progress.setVisible(True)
        self.log_area.clear()

        self.downloader = GuideDownloader(self.config)
        convert_pdf = self.chk_pdf.isChecked()

        thread = threading.Thread(
            target=self.downloader.download,
            args=(
                normalized_url,
                self.config.save_dir,
                self.config.language,
                self._log_threadsafe,
                lambda: self.log_signal.finished.emit(),
                convert_pdf,
            ),
            daemon=True,
            name="DownloadThread"
        )
        thread.start()

    def cancel_download(self):
        if self.downloader:
            self.downloader.cancel()
            self._log_threadsafe(
                get_text(self.config.language, "log_cancelled")
            )

    def _on_download_finished(self):
        lang = self.config.language
        self.btn_download.setEnabled(True)
        self.btn_download.setText(get_text(lang, "btn_download"))
        self.btn_cancel.setEnabled(False)
        self.progress.setVisible(False)

    # ==========================================
    # CLOSE
    # ==========================================

    def closeEvent(self, event):
        if self.downloader:
            self.downloader.cancel()
        self.config.save()
        event.accept()