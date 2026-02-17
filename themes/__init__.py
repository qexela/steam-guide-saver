"""Менеджер тем — с поддержкой EXE"""

import os
import logging

from paths import get_themes_dir

logger = logging.getLogger(__name__)


def load_theme(theme_name: str) -> str:
    themes_dir = get_themes_dir()
    qss_file = os.path.join(themes_dir, f"{theme_name}.qss")

    if not os.path.isfile(qss_file):
        logger.warning(f"Тема '{theme_name}' не найдена: {qss_file}")
        qss_file = os.path.join(themes_dir, "dark.qss")
        if not os.path.isfile(qss_file):
            logger.error("Тема dark.qss тоже не найдена!")
            return ""

    try:
        with open(qss_file, "r", encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        logger.error(f"Ошибка темы: {e}")
        return ""


def get_available_themes() -> list[str]:
    themes_dir = get_themes_dir()
    themes = []
    if os.path.isdir(themes_dir):
        for f in sorted(os.listdir(themes_dir)):
            if f.endswith('.qss'):
                themes.append(f[:-4])
    return themes if themes else ["dark"]