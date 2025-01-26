import os
import sys
import tempfile
import shutil
import pytest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from database import db, initialize_database

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
@pytest.fixture
def test_db_path():
    """一時的なテストデータベースのパスを提供する"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    # データベースパスを設定
    db.init(db_path)
    initialize_database()
    
    yield db_path
    
    # クリーンアップ
    try:
        os.unlink(db_path)
    except:
        pass

# テスト用の画像ファイル
@pytest.fixture(scope="session")
def test_image_path():
    return os.path.join(os.path.dirname(__file__), "fixtures", "images", "prithvi_prithvi.png")

# テスト用の音声ファイル
@pytest.fixture
def test_sound_path():
    """テスト用の音声ファイルパスを提供する"""
    return os.path.join(os.path.dirname(__file__), "fixtures", "sounds")

# テスト用の設定ファイル
@pytest.fixture(scope="function")
def test_settings_path(temp_dir):
    return os.path.join(temp_dir, "test_settings.json")
