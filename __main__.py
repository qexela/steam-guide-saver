"""
Steam Guide Saver — точка входа/entry point
"""

import sys
import os
import logging

from paths import get_log_path

# Логирование
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(get_log_path(), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main():
    try:
        from PyQt6.QtWidgets import QApplication
        from gui import MainWindow
        from icon_provider import setup_app_icon
        from about import APP_NAME, APP_VERSION

        logger.info(f"Запуск {APP_NAME} v{APP_VERSION}")

        # Windows: AppUserModelID (до QApplication)
        if sys.platform == 'win32':
            try:
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                    "steamguidesaver.classic.v2"
                )
            except Exception:
                pass

        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)

        window = MainWindow()
        setup_app_icon(app, window)
        window.show()

        sys.exit(app.exec())

    except ImportError as e:
        logger.critical(f"Зависимость: {e}")
        print(f"\n{e}")
        print("pip install PyQt6 requests beautifulsoup4 python-docx Pillow")
        sys.exit(1)

    except Exception as e:
        logger.critical(f"Ошибка: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()