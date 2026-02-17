"""Провайдер иконки — с поддержкой EXE"""

import os
import sys
import logging

from PyQt6.QtGui import (
    QIcon, QPixmap, QPainter, QColor, QFont,
    QPen, QBrush, QLinearGradient, QPolygonF
)
from PyQt6.QtCore import Qt, QRect, QPointF

from paths import get_assets_dir

logger = logging.getLogger(__name__)


def get_icon() -> QIcon:
    """Получить иконку: из файла или сгенерированную"""
    icon = _load_from_file()
    if icon and not icon.isNull():
        logger.info("Иконка из файла")
        return icon

    logger.info("Генерация встроенной иконки")
    return _generate_builtin_icon()


def _load_from_file() -> QIcon | None:
    assets_dir = get_assets_dir()
    candidates = [
        os.path.join(assets_dir, "icon.ico"),
        os.path.join(assets_dir, "icon.png"),
        os.path.join(assets_dir, "icon.svg"),
    ]

    for path in candidates:
        if os.path.isfile(path):
            try:
                icon = QIcon(path)
                if not icon.isNull():
                    logger.info(f"Иконка: {path}")
                    return icon
            except Exception as e:
                logger.warning(f"Ошибка иконки {path}: {e}")
    return None


def _generate_builtin_icon() -> QIcon:
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        pixmap = _draw_icon(size)
        icon.addPixmap(pixmap)
    return icon


def _draw_icon(size: int) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    s = size
    margin = max(1, s // 16)

    # Фон
    bg_rect = QRect(margin, margin, s - 2 * margin, s - 2 * margin)
    radius = max(2, s // 6)

    bg_gradient = QLinearGradient(0, 0, 0, s)
    bg_gradient.setColorAt(0.0, QColor(27, 40, 56))
    bg_gradient.setColorAt(1.0, QColor(15, 25, 40))

    painter.setPen(QPen(QColor(42, 71, 94), max(1, s // 32)))
    painter.setBrush(QBrush(bg_gradient))
    painter.drawRoundedRect(bg_rect, radius, radius)

    # Стрелка
    cx, cy = s / 2, s / 2
    arrow_w = s * 0.35
    arrow_h = s * 0.22
    shaft_w = s * 0.14
    shaft_h = s * 0.18
    bar_w = s * 0.45
    bar_h = max(2, s * 0.07)

    arrow_color = QColor(164, 208, 7)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(arrow_color))

    shaft_x = cx - shaft_w / 2
    shaft_y = cy - shaft_h - arrow_h * 0.3
    painter.drawRect(QRect(
        int(shaft_x), int(shaft_y), int(shaft_w), int(shaft_h)
    ))

    tip_y = shaft_y + shaft_h + arrow_h
    triangle = QPolygonF([
        QPointF(cx - arrow_w, shaft_y + shaft_h),
        QPointF(cx + arrow_w, shaft_y + shaft_h),
        QPointF(cx, tip_y),
    ])
    painter.drawPolygon(triangle)

    # Полоска
    bar_y = tip_y + s * 0.06
    painter.setBrush(QBrush(QColor(102, 192, 244)))
    painter.drawRoundedRect(QRect(
        int(cx - bar_w / 2), int(bar_y), int(bar_w), int(bar_h)
    ), max(1, s // 32), max(1, s // 32))

    # Буква S
    if s >= 48:
        font_size = max(6, s // 6)
        font = QFont("Arial", font_size, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QPen(QColor(200, 200, 220, 120)))
        letter_rect = QRect(
            s - margin - font_size - 2, margin + 1,
            font_size + 4, font_size + 4
        )
        painter.drawText(letter_rect, Qt.AlignmentFlag.AlignCenter, "S")

    painter.end()
    return pixmap


def setup_app_icon(app, window):
    """Установить иконку для приложения и окна"""
    icon = get_icon()
    window.setWindowIcon(icon)
    app.setWindowIcon(icon)

    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "steamguidesaver.classic.v2"
            )
        except Exception:
            pass