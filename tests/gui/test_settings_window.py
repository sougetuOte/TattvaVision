import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QSpinBox, QPushButton, QSlider
from i18n import i18n

def test_settings_window_components(main_window, qtbot):
    """設定ウィンドウの基本コンポーネントテスト"""
    # 設定ボタンを見つける
    settings_button = None
    for button in main_window.findChildren(QPushButton):
        if i18n.get('app.settings') in button.text():
            settings_button = button
            break
    assert settings_button is not None
    
    # ボタンをクリック
    qtbot.mouseClick(settings_button, Qt.LeftButton)
    
    # settings_windowが生成されていることを確認
    assert hasattr(main_window, 'settings_window')
    
    # 言語選択コンボボックスの存在確認
    language_combo = main_window.settings_window.findChild(QComboBox)
    assert language_combo is not None
    
    # 瞑想時間スピンボックスの存在確認
    time_spinbox = main_window.settings_window.findChild(QSpinBox)
    assert time_spinbox is not None

    # クリーンアップ
    if hasattr(main_window, 'settings_window'):
        main_window.settings_window.close()
