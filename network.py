"""Сетевой слой"""

import logging
import threading
from io import BytesIO
from urllib.parse import urlparse, parse_qs
from typing import Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import HEADERS, HAS_PILLOW, AppConfig

if HAS_PILLOW:
    from PIL import Image

logger = logging.getLogger(__name__)


class URLValidator:
    VALID_HOSTS = frozenset({'steamcommunity.com', 'www.steamcommunity.com'})
    REQUIRED_PATH = '/sharedfiles/filedetails/'

    @classmethod
    def validate(cls, url: str) -> Tuple[bool, str]:
        if not url or not url.strip():
            return False, "URL is empty"

        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        try:
            parsed = urlparse(url)
        except ValueError:
            return False, "Invalid URL format"

        hostname = parsed.hostname
        if not hostname or hostname not in cls.VALID_HOSTS:
            return False, f"Host '{hostname}' is not steamcommunity.com"

        if cls.REQUIRED_PATH not in (parsed.path or ''):
            return False, "URL is not a Steam guide link"

        params = parse_qs(parsed.query)
        ids = params.get('id', [])
        if not ids or not ids[0]:
            return False, "Guide ID not found in URL"

        guide_id = ids[0]
        if not guide_id.isdigit():
            return False, f"Invalid guide ID: '{guide_id}'"

        normalized = f"https://steamcommunity.com/sharedfiles/filedetails/?id={guide_id}"
        return True, normalized

    @classmethod
    def extract_guide_id(cls, url: str) -> Optional[str]:
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            ids = params.get('id', [])
            if ids and ids[0].isdigit():
                return ids[0]
        except (ValueError, IndexError):
            pass
        return None


def create_session(config: AppConfig) -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)
    retry_strategy = Retry(
        total=config.max_retries,
        backoff_factor=config.retry_backoff,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


class ImageCache:
    def __init__(self, max_size: int = 100):
        self._cache: dict[str, bytes] = {}
        self._order: list[str] = []
        self._max_size = max_size
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def get(self, url: str) -> Optional[BytesIO]:
        with self._lock:
            if url in self._cache:
                self._hits += 1
                self._order.remove(url)
                self._order.append(url)
                return BytesIO(self._cache[url])
            self._misses += 1
            return None

    def put(self, url: str, data: BytesIO):
        with self._lock:
            if url in self._cache:
                return
            while len(self._cache) >= self._max_size:
                oldest = self._order.pop(0)
                del self._cache[oldest]
            data.seek(0)
            self._cache[url] = data.read()
            self._order.append(url)
            data.seek(0)

    def clear(self):
        with self._lock:
            self._cache.clear()
            self._order.clear()

    @property
    def stats(self) -> str:
        with self._lock:
            total = self._hits + self._misses
            rate = (self._hits / total * 100) if total > 0 else 0
            return f"Cache: {len(self._cache)} items, hits={self._hits}, miss={self._misses}, rate={rate:.0f}%"


_image_cache = ImageCache()


def download_image(url, session=None, config=None, cache=None):
    if not url or not url.startswith('http'):
        return None
    if cache is None:
        cache = _image_cache
    if config is None:
        config = AppConfig()

    cached = cache.get(url)
    if cached:
        return cached

    req_session = session or requests
    max_size = config.max_image_size_mb * 1024 * 1024

    try:
        response = req_session.get(url, headers=HEADERS, stream=True, timeout=config.timeout)
        response.raise_for_status()
        content_type = response.headers.get('content-type', '')
        if 'image' not in content_type and 'octet-stream' not in content_type:
            return None
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > max_size:
            return None

        data = BytesIO(response.content)
        if data.getbuffer().nbytes == 0:
            return None
        if HAS_PILLOW:
            try:
                img = Image.open(data)
                img.verify()
                data.seek(0)
            except Exception:
                return None

        cache.put(url, data)
        data.seek(0)
        return data

    except (requests.Timeout, requests.HTTPError, requests.ConnectionError, requests.RequestException):
        pass
    except Exception as e:
        logger.error(f"Ошибка загрузки {url[:60]}: {e}")
    return None