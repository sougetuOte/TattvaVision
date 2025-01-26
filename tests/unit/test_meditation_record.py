import pytest
from datetime import datetime, timedelta
from database import MeditationRecord
from .test_database import database_connection

@pytest.mark.parametrize("duration,expected_status", [
    (5, "短時間瞑想"),
    (15, "通常瞑想"),
    (30, "長時間瞑想"),
])
def test_meditation_duration_status(test_db_path, duration, expected_status):
    """瞑想時間に基づくステータス分類のテスト"""
    with database_connection(test_db_path):
        # テストデータの作成
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration)
        
        record = MeditationRecord.create(
            date=start_time.date(),
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            card_name='テストカード',
            notes='テストメモ'
        )
        
        # ステータスの確認
        assert record.get_duration_status() == expected_status

@pytest.mark.parametrize("card_name,expected_element", [
    ("地のカード", "地"),
    ("水のカード", "水"),
    ("火のカード", "火"),
    ("風のカード", "風"),
    ("空のカード", "空"),
])
def test_card_element_mapping(test_db_path, card_name, expected_element):
    """カード名と元素のマッピングテスト"""
    with database_connection(test_db_path):
        record = MeditationRecord.create(
            date=datetime.now().date(),
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration=10,
            card_name=card_name,
            notes='テストメモ'
        )
        
        assert record.get_element() == expected_element

@pytest.mark.parametrize("notes,expected_keywords", [
    ("平和な気持ちになった", ["平和"]),
    ("集中力が高まり、安定感を感じた", ["集中", "安定"]),
    ("エネルギーが満ちてきた", ["エネルギー"]),
])
def test_meditation_keywords_extraction(test_db_path, notes, expected_keywords):
    """瞑想メモからのキーワード抽出テスト"""
    with database_connection(test_db_path):
        record = MeditationRecord.create(
            date=datetime.now().date(),
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration=10,
            card_name='テストカード',
            notes=notes
        )
        
        keywords = record.extract_keywords()
        for keyword in expected_keywords:
            assert keyword in keywords
