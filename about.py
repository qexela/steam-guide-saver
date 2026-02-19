"""
Информация о приложении и авторе
About the application and the author
"""

APP_NAME = "Steam Guide Saver"
APP_VERSION = "2.0.1"
APP_AUTHOR = "AlexeyQ"
APP_GITHUB = "https://github.com/qexela/steam-guide-saver"  # ← или ""
APP_YEAR = "2025"
APP_LICENSE = "MIT"
APP_DESCRIPTION = "Classic Steam Community Guide Downloader"

ABOUT_EN = f"""
<h2>{APP_NAME}</h2>
<p>Version: <b>{APP_VERSION}</b></p>
<p>{APP_DESCRIPTION}</p>
<hr>
<p>Author: <b>{APP_AUTHOR}</b></p>
<p>Year: {APP_YEAR}</p>
<p>License: {APP_LICENSE}</p>
{f'<p>GitHub: <a href="{APP_GITHUB}">{APP_GITHUB}</a></p>' if APP_GITHUB else ''}
<hr>
<p style="font-size:9pt; color:#888;">
Built with Python, PyQt6, BeautifulSoup4, python-docx
</p>
"""

ABOUT_RU = f"""
<h2>{APP_NAME}</h2>
<p>Версия: <b>{APP_VERSION}</b></p>
<p>{APP_DESCRIPTION}</p>
<hr>
<p>Автор: <b>{APP_AUTHOR}</b></p>
<p>Год: {APP_YEAR}</p>
<p>Лицензия: {APP_LICENSE}</p>
{f'<p>GitHub: <a href="{APP_GITHUB}">{APP_GITHUB}</a></p>' if APP_GITHUB else ''}
<hr>
<p style="font-size:9pt; color:#888;">
Создано с помощью Python, PyQt6, BeautifulSoup4, python-docx
</p>
"""


def get_about_text(lang: str) -> str:
    if lang == "ru":
        return ABOUT_RU
    return ABOUT_EN