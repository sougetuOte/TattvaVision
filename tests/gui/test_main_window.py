import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox, QPushButton
from i18n import i18n

def test_window_size(main_window):
    """メインウィンドウの初期サイズが正しく設定されているかテスト"""
    assert main_window.width() >= 1000
    assert main_window.height() >= 600

def test_has_buttons(main_window):
    """必要なボタンが存在するかテスト"""
    # 開始・停止ボタンの存在確認
    assert hasattr(main_window, 'start_button')
    assert hasattr(main_window, 'stop_button')
    
    # 設定ボタンの存在確認
    settings_button = None
    for button in main_window.findChildren(QPushButton):
        if i18n.get('app.settings') in button.text():
            settings_button = button
            break
    assert settings_button is not None
    
    # 記録一覧ボタンの存在確認
    record_button = None
    for button in main_window.findChildren(QPushButton):
        if i18n.get('record.list') in button.text():
            record_button = button
            break
    assert record_button is not None
