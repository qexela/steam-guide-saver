"""APP Config"""

import os
import json
import logging
from dataclasses import dataclass, field, asdict

from paths import get_config_path, get_app_dir

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
}

try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

AVAILABLE_THEMES = ["dark", "light", "steam", "cyberpunk"]


@dataclass
class AppConfig:
    language: str = "en"
    save_dir: str = field(
        default_factory=lambda: os.path.join(get_app_dir(), "Steam_Manuals")
    )
    theme: str = "dark"
    timeout: int = 15
    max_retries: int = 3
    retry_backoff: float = 0.5
    max_image_size_mb: int = 50
    max_image_width_inches: float = 6.0
    cell_image_width_inches: float = 1.8
    convert_to_pdf: bool = False

    def __post_init__(self):
        if self.language not in ("en", "ru"):
            self.language = "en"
        if self.timeout < 1:
            self.timeout = 15
        if self.max_retries < 0:
            self.max_retries = 3
        if self.theme not in AVAILABLE_THEMES:
            self.theme = "dark"

    @classmethod
    def load(cls) -> 'AppConfig':
        config_path = get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                known = {f for f in cls.__dataclass_fields__}
                filtered = {k: v for k, v in data.items() if k in known}
                config = cls(**filtered)
                logger.info(f"Конфиг: {config_path}")
                return config
            except (json.JSONDecodeError, TypeError, OSError) as e:
                logger.warning(f"Ошибка конфига: {e}")
        return cls()

    def save(self):
        config_path = get_config_path()
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, indent=2, ensure_ascii=False)
        except OSError as e:
            logger.error(f"Ошибка сохранения: {e}")