import pytest
import os
from datetime import datetime
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

def test_initialize_database(test_db_path):
    """データベースの初期化テスト"""
    with database_connection(test_db_path):
        # テーブルが作成されていることを確認
        assert MeditationRecord.table_exists()

def test_create_meditation_record(test_db_path):
    """瞑想記録の作成テスト"""
    with database_connection(test_db_path):
        # テストデータ
        test_time = datetime.now()
        test_record = {
            'date': test_time.date(),
            'start_time': test_time,
            'end_time': test_time,
            'duration': 10,
            'card_name': 'テストカード',
            'notes': 'テストメモ'
        }
        
        # レコードの作成
        record = MeditationRecord.create(**test_record)
        
        # 作成されたレコードの確認
        assert record.card_name == 'テストカード'
        assert record.duration == 10
        assert record.notes == 'テストメモ'

def test_retrieve_meditation_record(test_db_path):
    """瞑想記録の取得テスト"""
    with database_connection(test_db_path):
        # テストデータの作成
        test_time = datetime.now()
        test_record = MeditationRecord.create(
            date=test_time.date(),
            start_time=test_time,
            end_time=test_time,
            duration=15,
            card_name='テストカード2',
            notes='テストメモ2'
        )
        
        # レコードの取得
        retrieved_record = MeditationRecord.get_by_id(test_record.id)
        
        # 取得したレコードの確認
        assert retrieved_record.card_name == 'テストカード2'
        assert retrieved_record.duration == 15
        assert retrieved_record.notes == 'テストメモ2'

def test_update_meditation_record(test_db_path):
    """瞑想記録の更新テスト"""
    with database_connection(test_db_path):
        # テストデータの作成
        test_time = datetime.now()
        record = MeditationRecord.create(
            date=test_time.date(),
            start_time=test_time,
            end_time=test_time,
            duration=20,
            card_name='更新前',
            notes='メモ更新前'
        )
        
        # レコードの更新
        record.card_name = '更新後'
        record.notes = 'メモ更新後'
        record.save()
        
        # 更新されたレコードの確認
        updated_record = MeditationRecord.get_by_id(record.id)
        assert updated_record.card_name == '更新後'
        assert updated_record.notes == 'メモ更新後'

def test_delete_meditation_record(test_db_path):
    """瞑想記録の削除テスト"""
    with database_connection(test_db_path):
        # テストデータの作成
        test_time = datetime.now()
        record = MeditationRecord.create(
            date=test_time.date(),
            start_time=test_time,
            end_time=test_time,
            duration=25,
            card_name='削除テスト',
            notes='削除用メモ'
        )
        
        # レコードの削除
        record_id = record.id
        record.delete_instance()
        
        # レコードが削除されていることを確認
        with pytest.raises(MeditationRecord.DoesNotExist):
            MeditationRecord.get_by_id(record_id)
