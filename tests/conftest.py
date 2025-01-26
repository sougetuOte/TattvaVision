import os
import sys
import tempfile
import shutil
import pytest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from database import db, initialize_database

# テスト用のアプリケーションインスタンス
@pytest.fixture(scope="session")
def app(request):
    # ヘッドレスモードを確実に設定
    os.environ["QT_QPA_PLATFORM"] = "minimal"
    
    # 既存のアプリケーションインスタンスがあれば使用
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # セッション終了時のクリーンアップ
    def cleanup():
        app.quit()
    request.addfinalizer(cleanup)
    
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

# GUIテスト用のメインウィンドウ
@pytest.fixture
def main_window(app, test_db_path, test_settings_path, request):
    """テスト用のメインウィンドウインスタンスを提供する"""
    from tattva_app import TattvaApp
    window = TattvaApp()
    
    # テスト終了時のクリーンアップ
    def cleanup():
        window.close()
        window.deleteLater()
    request.addfinalizer(cleanup)
    
    return window

# GUIテスト用のQTestライブラリ
@pytest.fixture
def qtbot(app):
    """QTestライブラリのインスタンスを提供する"""
    from pytestqt.qtbot import QtBot
    return QtBot(app)
