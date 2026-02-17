import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network import URLValidator


class TestURLValidator:
    def test_valid_url(self):
        ok, r = URLValidator.validate("https://steamcommunity.com/sharedfiles/filedetails/?id=123")
        assert ok and "id=123" in r

    def test_auto_scheme(self):
        ok, r = URLValidator.validate("steamcommunity.com/sharedfiles/filedetails/?id=456")
        assert ok and r.startswith("https://")

    def test_empty(self):
        ok, _ = URLValidator.validate("")
        assert not ok

    def test_wrong_host(self):
        ok, _ = URLValidator.validate("https://google.com")
        assert not ok

    def test_no_id(self):
        ok, _ = URLValidator.validate("https://steamcommunity.com/sharedfiles/filedetails/")
        assert not ok

    def test_non_numeric_id(self):
        ok, _ = URLValidator.validate("https://steamcommunity.com/sharedfiles/filedetails/?id=abc")
        assert not ok

    def test_extract_id(self):
        assert URLValidator.extract_guide_id("https://steamcommunity.com/sharedfiles/filedetails/?id=42") == "42"
        assert URLValidator.extract_guide_id("https://google.com") is None