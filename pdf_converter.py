"""
Конвертация DOCX → PDF
Поддерживает:
1. LibreOffice (кроссплатформ)
2. MS Word через win32com (Windows)
3. MS Word через comtypes (Windows, fallback)
4. docx2pdf (если установлен)
"""

import os
import sys
import subprocess
import logging
import shutil

logger = logging.getLogger(__name__)


# ============================================================
# ПРОВЕРКА ДОСТУПНЫХ КОНВЕРТЕРОВ
# ============================================================

def check_available_converters() -> dict[str, bool]:
    """Проверяет какие конвертеры доступны в системе"""
    result = {
        "libreoffice": False,
        "win32com": False,
        "comtypes": False,
        "docx2pdf": False,
    }

    # LibreOffice
    result["libreoffice"] = find_libreoffice() is not None

    # win32com (предпочтительный способ для Windows)
    if sys.platform == 'win32':
        try:
            import win32com.client
            result["win32com"] = True
        except ImportError:
            pass

        # comtypes (fallback)
        try:
            import comtypes.client
            result["comtypes"] = True
        except ImportError:
            pass

    # docx2pdf
    try:
        import docx2pdf
        result["docx2pdf"] = True
    except ImportError:
        pass

    logger.info(f"Доступные PDF-конвертеры: {result}")
    return result


def get_install_instructions() -> str:
    """Инструкции по установке конвертера"""
    if sys.platform == 'win32':
        return (
            "Для конвертации в PDF установите один из вариантов:\n\n"
            "Вариант 1 (рекомендуется):\n"
            "  pip install pywin32\n\n"
            "Вариант 2:\n"
            "  pip install docx2pdf\n\n"
            "Вариант 3:\n"
            "  pip install comtypes\n\n"
            "Вариант 4:\n"
            "  Установите LibreOffice: https://www.libreoffice.org/download/"
        )
    elif sys.platform == 'darwin':
        return (
            "Для конвертации в PDF установите один из вариантов:\n\n"
            "Вариант 1:\n"
            "  pip install docx2pdf\n"
            "  (требует MS Word для Mac)\n\n"
            "Вариант 2:\n"
            "  Установите LibreOffice:\n"
            "  brew install --cask libreoffice"
        )
    else:
        return (
            "Для конвертации в PDF:\n\n"
            "  sudo apt install libreoffice\n"
            "  # или\n"
            "  sudo dnf install libreoffice"
        )


# ============================================================
# LIBREOFFICE
# ============================================================

def find_libreoffice() -> str | None:
    """Ищет путь к LibreOffice"""
    # В PATH
    for name in ("libreoffice", "soffice"):
        path = shutil.which(name)
        if path:
            return path

    # Windows — стандартные пути
    if sys.platform == 'win32':
        candidates = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]
        # Поиск по Program Files
        for pf in [os.environ.get("ProgramFiles", ""), os.environ.get("ProgramFiles(x86)", "")]:
            if pf:
                lo_path = os.path.join(pf, "LibreOffice", "program", "soffice.exe")
                if lo_path not in candidates:
                    candidates.append(lo_path)

        for path in candidates:
            if os.path.isfile(path):
                logger.info(f"LibreOffice найден: {path}")
                return path

    # macOS
    if sys.platform == 'darwin':
        mac_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
        if os.path.isfile(mac_path):
            return mac_path

    return None


def convert_with_libreoffice(docx_path: str, output_dir: str) -> str | None:
    """Конвертация через LibreOffice CLI"""
    lo_path = find_libreoffice()
    if not lo_path:
        logger.debug("LibreOffice не найден")
        return None

    try:
        logger.info(f"Конвертация через LibreOffice: {lo_path}")

        cmd = [
            lo_path,
            '--headless',
            '--norestore',
            '--convert-to', 'pdf',
            '--outdir', output_dir,
            os.path.abspath(docx_path)
        ]

        # На Windows скрываем окно консоли
        creationflags = 0
        if sys.platform == 'win32':
            creationflags = subprocess.CREATE_NO_WINDOW

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=output_dir,
            creationflags=creationflags
        )

        if result.returncode == 0:
            base = os.path.splitext(os.path.basename(docx_path))[0]
            pdf_path = os.path.join(output_dir, f"{base}.pdf")
            if os.path.isfile(pdf_path):
                logger.info(f"LibreOffice: PDF создан: {pdf_path}")
                return pdf_path
            else:
                logger.warning(f"LibreOffice завершился успешно, но PDF не найден: {pdf_path}")

        logger.error(f"LibreOffice returncode={result.returncode}")
        if result.stderr:
            logger.error(f"LibreOffice stderr: {result.stderr[:500]}")
        if result.stdout:
            logger.debug(f"LibreOffice stdout: {result.stdout[:500]}")

        return None

    except subprocess.TimeoutExpired:
        logger.error("LibreOffice: таймаут 120с")
        return None
    except FileNotFoundError:
        logger.error(f"LibreOffice не найден по пути: {lo_path}")
        return None
    except Exception as e:
        logger.error(f"LibreOffice ошибка: {e}")
        return None


# ============================================================
# MS WORD через win32com (предпочтительный для Windows)
# ============================================================

def convert_with_win32com(docx_path: str) -> str | None:
    """Конвертация через MS Word COM с pywin32"""
    if sys.platform != 'win32':
        return None

    try:
        import win32com.client
        import pythoncom
    except ImportError:
        logger.debug("pywin32 (win32com) не установлен")
        return None

    word = None
    try:
        logger.info("Конвертация через MS Word (win32com)...")

        # Инициализация COM в текущем потоке
        pythoncom.CoInitialize()

        word = win32com.client.Dispatch('Word.Application')
        word.Visible = False
        word.DisplayAlerts = False

        abs_path = os.path.abspath(docx_path)
        pdf_path = os.path.splitext(abs_path)[0] + '.pdf'

        doc = word.Documents.Open(abs_path)
        doc.SaveAs(pdf_path, FileFormat=17)  # 17 = wdFormatPDF
        doc.Close(False)

        if os.path.isfile(pdf_path):
            logger.info(f"MS Word (win32com): PDF создан: {pdf_path}")
            return pdf_path

        logger.warning("MS Word: PDF файл не создан")
        return None

    except Exception as e:
        logger.error(f"MS Word (win32com) ошибка: {e}")
        return None
    finally:
        if word:
            try:
                word.Quit()
            except Exception:
                pass
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


# ============================================================
# MS WORD через comtypes (fallback)
# ============================================================

def convert_with_comtypes(docx_path: str) -> str | None:
    """Конвертация через MS Word COM с comtypes"""
    if sys.platform != 'win32':
        return None

    try:
        import comtypes.client
    except ImportError:
        logger.debug("comtypes не установлен")
        return None

    word = None
    try:
        logger.info("Конвертация через MS Word (comtypes)...")

        word = comtypes.client.CreateObject('Word.Application')
        word.Visible = False

        abs_path = os.path.abspath(docx_path)
        pdf_path = os.path.splitext(abs_path)[0] + '.pdf'

        doc = word.Documents.Open(abs_path)
        doc.SaveAs(pdf_path, FileFormat=17)
        doc.Close()

        if os.path.isfile(pdf_path):
            logger.info(f"MS Word (comtypes): PDF создан: {pdf_path}")
            return pdf_path

        return None

    except Exception as e:
        logger.error(f"MS Word (comtypes) ошибка: {e}")
        return None
    finally:
        if word:
            try:
                word.Quit()
            except Exception:
                pass


# ============================================================
# docx2pdf (кроссплатформ, требует Word/LibreOffice)
# ============================================================

def convert_with_docx2pdf(docx_path: str) -> str | None:
    """Конвертация через библиотеку docx2pdf"""
    try:
        from docx2pdf import convert
    except ImportError:
        logger.debug("docx2pdf не установлен")
        return None

    try:
        logger.info("Конвертация через docx2pdf...")

        abs_path = os.path.abspath(docx_path)
        pdf_path = os.path.splitext(abs_path)[0] + '.pdf'

        convert(abs_path, pdf_path)

        if os.path.isfile(pdf_path):
            logger.info(f"docx2pdf: PDF создан: {pdf_path}")
            return pdf_path

        return None

    except Exception as e:
        logger.error(f"docx2pdf ошибка: {e}")
        return None


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def convert_docx_to_pdf(docx_path: str, log_func=None) -> tuple[bool, str]:
    """
    Конвертирует DOCX в PDF, пробуя все доступные способы.

    Args:
        docx_path: Путь к DOCX-файлу
        log_func: Функция для логирования прогресса

    Returns:
        (success, pdf_path_or_error_message)
    """
    if log_func is None:
        log_func = lambda msg: None

    if not os.path.isfile(docx_path):
        return False, f"File not found: {docx_path}"

    output_dir = os.path.dirname(os.path.abspath(docx_path))

    # Список конвертеров в порядке приоритета
    converters = [
        ("LibreOffice", lambda: convert_with_libreoffice(docx_path, output_dir)),
        ("MS Word (win32com)", lambda: convert_with_win32com(docx_path)),
        ("MS Word (comtypes)", lambda: convert_with_comtypes(docx_path)),
        ("docx2pdf", lambda: convert_with_docx2pdf(docx_path)),
    ]

    errors = []

    for name, converter_func in converters:
        log_func(f"  Trying: {name}...")
        logger.info(f"Попытка конвертации через {name}...")

        try:
            pdf_path = converter_func()
            if pdf_path and os.path.isfile(pdf_path):
                return True, pdf_path
            else:
                msg = f"{name}: converter returned no result"
                logger.debug(msg)
                errors.append(msg)
        except Exception as e:
            msg = f"{name}: {e}"
            logger.error(msg)
            errors.append(msg)

    # Ничего не сработало
    instructions = get_install_instructions()
    error_details = "\n".join(f"  • {e}" for e in errors)

    error_msg = (
        f"No PDF converter available.\n\n"
        f"Tried:\n{error_details}\n\n"
        f"{instructions}"
    )

    logger.error(f"PDF конвертация не удалась. Детали:\n{error_details}")
    return False, error_msg