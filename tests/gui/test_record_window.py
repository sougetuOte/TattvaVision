import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QPushButton
from i18n import i18n

def test_record_window_components(main_window, qtbot):
    """記録ウィンドウの基本コンポーネントテスト"""
    # 記録一覧ボタンを見つける
    record_button = None
    for button in main_window.findChildren(QPushButton):
        if i18n.get('record.list') in button.text():
            record_button = button
            break
    assert record_button is not None
    
    # ボタンをクリック
    qtbot.mouseClick(record_button, Qt.LeftButton)
    
    # ウィンドウが表示されていることを確認
    assert hasattr(main_window, 'record_window')
    assert main_window.record_window.isVisible()
    
    # テーブルウィジェットの存在確認
    table = main_window.record_window.findChild(QTableWidget)
    assert table is not None
