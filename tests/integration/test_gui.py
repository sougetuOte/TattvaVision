import pytest
import os
from datetime import datetime, timedelta
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from tattva_app import TattvaApp
from database import initialize_database, MeditationRecord, db
from contextlib import contextmanager

@contextmanager
def database_connection(db_path):
    """データベース接続のコンテキストマネージャ"""
    if os.path.exists(db_path):
        os.remove(db_path)
    db.init(db_path)
    initialize_database()
    try:
        yield
    finally:
        db.close()

def test_app_initialization(app, test_db_path):
    """アプリケーションの初期化テスト"""
    with database_connection(test_db_path):
        # メインウィンドウの作成
        window = TattvaApp()
        
        # 基本的なUIコンポーネントの存在確認
        assert window.card_combo is not None
        assert window.timer_spinbox is not None
        assert window.start_button is not None
        assert window.stop_button is not None
        assert window.notes is not None

def test_meditation_timer(app, test_db_path):
    """瞑想タイマーの動作テスト"""
    with database_connection(test_db_path):
        # メインウィンドウの作成
        window = TattvaApp()
        
        # タイマーの初期設定
        window.timer_spinbox.setValue(1)  # 1分に設定
        
        # 開始ボタンの状態確認
        assert window.start_button.isEnabled()
        assert not window.stop_button.isEnabled()
        
        # 瞑想開始時刻を設定
        window.meditation_start_time = datetime.now()
        
        # 瞑想開始
        QTest.mouseClick(window.start_button, Qt.LeftButton)
        
        # 少し待機
        QTest.qWait(100)
        
        # ボタンの状態確認
        assert not window.start_button.isEnabled()
        assert window.stop_button.isEnabled()
        
        # 瞑想終了時刻を設定
        window.meditation_end_time = window.meditation_start_time + timedelta(minutes=1)
        
        # タイマーの停止
        QTest.mouseClick(window.stop_button, Qt.LeftButton)
        
        # ボタンの状態確認
        assert window.start_button.isEnabled()
        assert not window.stop_button.isEnabled()

def test_record_saving(app, test_db_path):
    """記録保存機能のテスト"""
    with database_connection(test_db_path):
        # メインウィンドウの作成
        window = TattvaApp()
        
        # テストデータの設定
        window.card_combo.setCurrentText(window.card_combo.itemText(0))
        window.notes.setPlainText("テストメモ")
        
        # 瞑想の開始と終了時刻を設定
        window.meditation_start_time = datetime.now()
        window.meditation_end_time = window.meditation_start_time + timedelta(minutes=1)
        
        # 記録の保存
        window.save_meditation()
        
        # 保存されたレコードの確認
        record = MeditationRecord.select().order_by(MeditationRecord.id.desc()).first()
        assert record is not None
        assert record.notes == "テストメモ"
        assert record.card_name == window.card_combo.currentText()

def test_card_display(app, test_db_path):
    """カード表示機能のテスト"""
    with database_connection(test_db_path):
        # メインウィンドウの作成
        window = TattvaApp()
        
        # カードの選択
        initial_card = window.card_combo.currentText()
        window.update_card_display()
        
        # 解釈テキストの存在確認
        assert window.pos_interpret.text() != ""
        assert window.neg_interpret.text() != ""
        
        # カード画像の表示確認
        assert window.card_image.pixmap() is not None
