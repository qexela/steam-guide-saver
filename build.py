"""
Скрипт сборки EXE через PyInstaller.
Запуск: python build.py
"""

import subprocess
import sys
import os
import shutil

APP_NAME = "SteamGuideSaver"
MAIN_SCRIPT = "__main__.py"
ICON_FILE = os.path.join("assets", "icon.ico")

def build():
    # Базовая команда
    cmd = [
        sys.executable, "-m", "PyInstaller",

        # === Один файл ===
        "--onefile",

        # === Без консоли (GUI) ===
        "--windowed",
        "--noconsole",

        # === Имя выходного файла ===
        "--name", APP_NAME,

        # === Иконка (если есть) ===
    ]

    if os.path.isfile(ICON_FILE):
        cmd.extend(["--icon", ICON_FILE])
        print(f"✓ Иконка: {ICON_FILE}")
    else:
        print("⚠ Иконка не найдена, будет стандартная")

    # === Добавляем файлы данных ===

    # Темы QSS
    if os.path.isdir("themes"):
        # Формат: --add-data "source;destination" (Windows)
        # Формат: --add-data "source:destination" (Linux/Mac)
        sep = ";" if sys.platform == "win32" else ":"
        cmd.extend(["--add-data", f"themes{sep}themes"])
        print("✓ Темы включены")

    # Папка assets
    if os.path.isdir("assets"):
        sep = ";" if sys.platform == "win32" else ":"
        cmd.extend(["--add-data", f"assets{sep}assets"])
        print("✓ Assets включены")

    # === Скрытые импорты (на всякий случай) ===
    hidden_imports = [
        "PyQt6.QtWidgets",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "bs4",
        "docx",
        "PIL",
        "requests",
    ]
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])

    # === Главный скрипт ===
    cmd.append(MAIN_SCRIPT)

    print(f"\n{'='*50}")
    print(f"Сборка: {APP_NAME}")
    print(f"Команда: {' '.join(cmd)}")
    print(f"{'='*50}\n")

    # Запуск
    result = subprocess.run(cmd)

    if result.returncode == 0:
        # Определяем путь к exe
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
            print(f"\n⚠ Файл не найден: {exe_path}")
    else:
        print(f"\n❌ ERROR (код {result.returncode})")

    # Очистка
    cleanup = input("\nDel build/ и .spec? (y/n): ").strip().lower()
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