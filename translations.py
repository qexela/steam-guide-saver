"""Переводы интерфейса"""

TRANSLATIONS = {
    "en": {
        "window_title": "Steam Guide Saver",
        "app_subtitle": "Classic Steam Community Guide Downloader",
        "lbl_url": "Steam Guide URL:",
        "lbl_path": "Save Folder:",
        "btn_browse": "Browse...",
        "btn_download": "⬇  Download DOCX",
        "btn_downloading": "⏳  Downloading...",
        "btn_cancel": "✕  Cancel",
        "btn_clear_log": "🗑  Clear Log",
        "chk_pdf": "Also convert to PDF",
        "lbl_log": "Log:",
        "lbl_theme": "Theme:",
        "lbl_lang": "Language:",
        "err_no_url": "Please enter a URL.",
        "err_bad_url": (
            "Not a valid Steam guide URL.\n\n"
            "Expected:\n"
            "https://steamcommunity.com/sharedfiles/filedetails/?id=XXXXXX"
        ),
        "err_bad_path": "Invalid save path.\nFolder does not exist and cannot be created.",
        "err_path_not_writable": "Save folder is not writable.",
        "err_net_connection": "No internet connection or Steam is unavailable.",
        "err_net_timeout": "Connection timed out.",
        "err_access": "Access error (HTTP {}). Guide may be private.",
        "err_content": "Guide content not found on the page.",
        "err_permission": "File is locked! Close Word and retry.",
        "err_creating_dir": "Error creating folder:",
        "err_pdf_failed": "PDF conversion failed:",
        "err_pdf_no_support": "PDF conversion requires LibreOffice or MS Word installed.",
        "log_start": "Connecting to: {}...",
        "log_success": "\n✅ SUCCESS! File saved:\n{}",
        "log_pdf_success": "✅ PDF saved: {}",
        "log_pdf_converting": "Converting to PDF...",
        "log_cancelled": "Download cancelled.",
        "log_sections_found": "Found {} sections",
        "log_processing": "Processing: {}",
        "log_file_target": "Target: {}",
        "err_net": "Network error:",
        "msg_error": "Error",
        "msg_warning": "Warning",
        "msg_validation_title": "Validation Error",
        "ctx_paste": "Paste",
        "ctx_copy_all": "Copy Log",
        "menu_file": "File",
        "menu_help": "Help",
        "menu_about": "About",
        "menu_exit": "Exit",
    },
    "ru": {
        "window_title": "Загрузчик руководств Steam",
        "app_subtitle": "Классический загрузчик руководств Steam",
        "lbl_url": "Ссылка на руководство Steam:",
        "lbl_path": "Папка сохранения:",
        "btn_browse": "Обзор...",
        "btn_download": "⬇  Скачать DOCX",
        "btn_downloading": "⏳  Скачивание...",
        "btn_cancel": "✕  Отмена",
        "btn_clear_log": "🗑  Очистить лог",
        "chk_pdf": "Также конвертировать в PDF",
        "lbl_log": "Лог:",
        "lbl_theme": "Тема:",
        "lbl_lang": "Язык:",
        "err_no_url": "Введите ссылку.",
        "err_bad_url": (
            "Это не ссылка на руководство Steam.\n\n"
            "Ожидается:\n"
            "https://steamcommunity.com/sharedfiles/filedetails/?id=XXXXXX"
        ),
        "err_bad_path": "Неверный путь сохранения.\nПапка не существует и не может быть создана.",
        "err_path_not_writable": "Папка сохранения недоступна для записи.",
        "err_net_connection": "Нет интернета или Steam недоступен.",
        "err_net_timeout": "Время ожидания истекло.",
        "err_access": "Ошибка доступа (HTTP {}). Руководство может быть приватным.",
        "err_content": "Контент руководства не найден.",
        "err_permission": "Файл занят! Закройте Word и попробуйте снова.",
        "err_creating_dir": "Ошибка создания папки:",
        "err_pdf_failed": "Ошибка конвертации в PDF:",
        "err_pdf_no_support": "Для конвертации в PDF необходим LibreOffice или MS Word.",
        "log_start": "Подключение к: {}...",
        "log_success": "\n✅ ГОТОВО! Файл сохранён:\n{}",
        "log_pdf_success": "✅ PDF сохранён: {}",
        "log_pdf_converting": "Конвертация в PDF...",
        "log_cancelled": "Загрузка отменена.",
        "log_sections_found": "Найдено секций: {}",
        "log_processing": "Обработка: {}",
        "log_file_target": "Целевой файл: {}",
        "err_net": "Ошибка сети:",
        "msg_error": "Ошибка",
        "msg_warning": "Предупреждение",
        "msg_validation_title": "Ошибка валидации",
        "ctx_paste": "Вставить",
        "ctx_copy_all": "Копировать весь лог",
        "menu_file": "Файл",
        "menu_help": "Справка",
        "menu_about": "О программе",
        "menu_exit": "Выход",
    }
}


def get_text(lang_code: str, key: str, *args) -> str:
    lang_dict = TRANSLATIONS.get(lang_code, TRANSLATIONS["en"])
    template = lang_dict.get(key, key)
    if args:
        try:
            return template.format(*args)
        except (IndexError, KeyError):
            return template
    return template