"""
Определение путей — работает и в обычном Python, и в EXE
"""

import os
import sys


def get_base_dir() -> str:
    """
    Возвращает базовую директорию приложения.
    - Обычный запуск: папка с __main__.py
    - PyInstaller EXE: временная папка _MEIPASS
    """
    if getattr(sys, 'frozen', False):
        # Запущено как EXE (PyInstaller)
        return sys._MEIPASS
    else:
        # Обычный Python
        return os.path.dirname(os.path.abspath(__file__))


def get_app_dir() -> str:
    """
    Директория рядом с EXE (для сохранения настроек).
    - Обычный запуск: текущая рабочая директория
    - EXE: папка, где лежит .exe файл
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.getcwd()


def get_resource_path(relative_path: str) -> str:
    """
    Получить абсолютный путь к ресурсу (тема, иконка).
    Работает и в dev-режиме, и в собранном EXE.
    """
    base = get_base_dir()
    return os.path.join(base, relative_path)


def get_themes_dir() -> str:
    """Путь к папке с темами"""
    return get_resource_path("themes")


def get_assets_dir() -> str:
    """Путь к папке с ассетами"""
    return get_resource_path("assets")


def get_config_path() -> str:
    """Путь к файлу настроек (рядом с exe или в cwd)"""
    return os.path.join(get_app_dir(), "settings.json")


def get_log_path() -> str:
    """Путь к файлу логов"""
    return os.path.join(get_app_dir(), "downloader.log")