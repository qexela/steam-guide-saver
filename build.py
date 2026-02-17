"""
Скрипт сборки EXE через PyInstaller
Запуск: python build.py
"""

import subprocess
import sys
import os
import shutil

APP_NAME = "SteamGuideSaver"
MAIN_SCRIPT = "__main__.py"
ICON_FILE = os.path.join("assets", "icon.ico")
ICON_PNG = os.path.join("assets", "icon.png")

def ensure_icon():
    """Проверяет наличие .ico, конвертирует из .png если нужно"""
    if os.path.isfile(ICON_FILE):
        print(f"✓ Иконка найдена: {ICON_FILE}")
        return True

    if os.path.isfile(ICON_PNG):
        print(f"⚠ Файл .ico не найден, конвертирую из .png...")
        try:
            from PIL import Image
            img = Image.open(ICON_PNG)
            sizes = [(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)]
            img.save(ICON_FILE, format="ICO", sizes=sizes)
            print(f"✓ Создан: {ICON_FILE}")
            return True
        except ImportError:
            print("⚠ Pillow не установлен, иконка будет стандартная")
            return False
        except Exception as e:
            print(f"⚠ Ошибка конвертации: {e}")
            return False

    print("⚠ Иконка не найдена, будет стандартная")
    return False


def build():
    has_icon = ensure_icon()

    sep = ";" if sys.platform == "win32" else ":"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--noconsole",
        "--name", APP_NAME,
    ]

    # Иконка
    if has_icon:
        cmd.extend(["--icon", ICON_FILE])

    # Данные
    if os.path.isdir("themes"):
        cmd.extend(["--add-data", f"themes{sep}themes"])
        print("✓ Темы включены")

    if os.path.isdir("assets"):
        cmd.extend(["--add-data", f"assets{sep}assets"])
        print("✓ Assets включены")

    # Скрытые импорты
    hidden = [
        "PyQt6.QtWidgets",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "bs4",
        "docx",
        "PIL",
        "requests",
        "lxml",
    ]
    for imp in hidden:
        cmd.extend(["--hidden-import", imp])

    cmd.append(MAIN_SCRIPT)

    print(f"\n{'='*50}")
    print(f"Сборка: {APP_NAME}")
    print(f"{'='*50}\n")

    result = subprocess.run(cmd)

    if result.returncode == 0:
        if sys.platform == "win32":
            exe_path = os.path.join("dist", f"{APP_NAME}.exe")
        else:
            exe_path = os.path.join("dist", APP_NAME)

        if os.path.isfile(exe_path):
            size_mb = os.path.getsize(exe_path) / 1024 / 1024
            print(f"\n{'='*50}")
            print(f"✅ УСПЕХ!")
            print(f"Файл: {os.path.abspath(exe_path)}")
            print(f"Размер: {size_mb:.1f} MB")
            print(f"{'='*50}")
    else:
        print(f"\n❌ Ошибка сборки (код {result.returncode})")

    cleanup = input("\nУдалить build/ и .spec? (y/n): ").strip().lower()
    if cleanup == 'y':
        for d in ["build", "__pycache__"]:
            if os.path.isdir(d):
                shutil.rmtree(d)
                print(f"  Удалено: {d}/")
        for f in os.listdir("."):
            if f.endswith(".spec"):
                os.remove(f)
                print(f"  Удалено: {f}")


if __name__ == "__main__":
    build()