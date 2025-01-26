import os
import sys
import tempfile
import shutil
import pytest
from pathlib import Path
from PySide6.QtWidgets import QApplication

# テスト用のアプリケーションインスタンス
@pytest.fixture(scope="session")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

# テスト用の一時ディレクトリ
@pytest.fixture(scope="function")
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

# テスト用のデータベースパス
@pytest.fixture(scope="function")
def test_db_path(temp_dir):
    db_path = os.path.join(temp_dir, "test.db")
    yield db_path

# テスト用の画像ファイル
@pytest.fixture(scope="session")
def test_image_path():
    return os.path.join(os.path.dirname(__file__), "fixtures", "images", "prithvi_prithvi.png")

# テスト用の音声ファイル
@pytest.fixture(scope="session")
def test_sound_path():
    return os.path.join(os.path.dirname(__file__), "fixtures", "sounds", "test_bell.mp3")

# テスト用の設定ファイル
@pytest.fixture(scope="function")
def test_settings_path(temp_dir):
    return os.path.join(temp_dir, "test_settings.json")
