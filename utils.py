"""Вспомогательные функции"""

import re
import os
import logging

from docx.shared import RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

logger = logging.getLogger(__name__)


def clean_filename(title: str) -> str:
    if not title:
        return ""
    cleaned = re.sub(r'[\\/*?:"<>|]', "", title)
    cleaned = re.sub(r'[\x00-\x1f\x7f]', "", cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = cleaned[:200]
    cleaned = cleaned.rstrip('. ')
    return cleaned


def validate_save_path(path: str) -> tuple[bool, str]:
    """
    Валидация пути сохранения.
    Returns: (is_valid, error_message_or_normalized_path)
    """
    if not path or not path.strip():
        return False, "Path is empty"

    path = path.strip()
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.normpath(path)

    # Проверка на запрещённые символы (Windows)
    if os.name == 'nt':
        invalid_chars = re.findall(r'[*?"<>|]', path)
        if invalid_chars:
            return False, f"Invalid characters in path: {''.join(set(invalid_chars))}"

    # Если папка существует — проверяем права записи
    if os.path.exists(path):
        if not os.path.isdir(path):
            return False, "Path is not a directory"
        if not os.access(path, os.W_OK):
            return False, "Directory is not writable"
        return True, path

    # Если не существует — пробуем создать
    try:
        os.makedirs(path, exist_ok=True)
        return True, path
    except OSError as e:
        return False, f"Cannot create directory: {e}"


def add_horizontal_line(paragraph):
    try:
        pPr = paragraph._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), 'auto')
        pBdr.append(bottom)
        pPr.append(pBdr)
    except Exception as e:
        logger.warning(f"Ошибка горизонтальной линии: {e}")


def add_hyperlink(paragraph, url, text, color=None, underline=True):
    if color is None:
        color = RGBColor(0x05, 0x63, 0xC1)

    if not url:
        return paragraph.add_run(text)

    try:
        part = paragraph.part
        r_id = part.relate_to(
            url,
            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
            is_external=True
        )
        hyperlink = OxmlElement('w:hyperlink')
        hyperlink.set(qn('r:id'), r_id)
        new_run = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')
        if color:
            c_elem = OxmlElement('w:color')
            c_elem.set(qn('w:val'), color.rgb if hasattr(color, 'rgb') else "0563C1")
            rPr.append(c_elem)
        if underline:
            u = OxmlElement('w:u')
            u.set(qn('w:val'), 'single')
            rPr.append(u)
        new_run.append(rPr)
        new_run.text = text
        hyperlink.append(new_run)
        paragraph._p.append(hyperlink)
        return hyperlink
    except Exception as e:
        logger.warning(f"Ошибка гиперссылки '{url}': {e}")
        run = paragraph.add_run(text)
        if color:
            run.font.color.rgb = color
        return run