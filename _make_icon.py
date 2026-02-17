"""
Конвертирует icon.png → icon.ico для PyInstaller
Запуск: python _make_icon.py
"""

from PIL import Image
import os

png_path = os.path.join("assets", "icon.png")
ico_path = os.path.join("assets", "icon.ico")

if not os.path.isfile(png_path):
    print(f"Файл не найден: {png_path}")
    exit(1)

img = Image.open(png_path)

# ICO содержит несколько размеров
sizes = [
    (16, 16),
    (24, 24),
    (32, 32),
    (48, 48),
    (64, 64),
    (128, 128),
    (256, 256),
]

img.save(
    ico_path,
    format="ICO",
    sizes=sizes,
)

print(f"✅ Создан: {ico_path}")
print(f"   Размеры: {[f'{s[0]}x{s[1]}' for s in sizes]}")
print(f"   Теперь пересоберите EXE: python build.py")