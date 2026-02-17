import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import clean_filename, validate_save_path
from docx_builder import StyleContext


class TestCleanFilename:
    def test_normal(self):
        assert clean_filename("My Guide") == "My Guide"

    def test_special(self):
        r = clean_filename('Test: "2" <3>')
        assert ':' not in r and '"' not in r

    def test_empty(self):
        assert clean_filename("") == ""

    def test_long(self):
        assert len(clean_filename("A" * 300)) <= 200


class TestStyleContext:
    def test_default(self):
        ctx = StyleContext()
        assert not any([ctx.bold, ctx.italic, ctx.underline])

    def test_copy(self):
        ctx = StyleContext(bold=True)
        copy = ctx.copy()
        copy.italic = True
        assert ctx.bold and not ctx.italic


class TestValidatePath:
    def test_valid_existing(self, tmp_path):
        ok, result = validate_save_path(str(tmp_path))
        assert ok

    def test_empty(self):
        ok, _ = validate_save_path("")
        assert not ok

    def test_creatable(self, tmp_path):
        new_dir = str(tmp_path / "new_folder")
        ok, result = validate_save_path(new_dir)
        assert ok
        assert os.path.isdir(result)