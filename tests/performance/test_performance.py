import pytest
import time
from datetime import datetime, timedelta
from database import initialize_database, MeditationRecord, db
from ..unit.test_database import database_connection

def test_database_bulk_insert(test_db_path):
    """大量レコード挿入のパフォーマンステスト"""
    with database_connection(test_db_path):
        start_time = time.time()
        records = []
        base_time = datetime.now()
        
        # 1000件のレコードを作成
        for i in range(1000):
            record_time = base_time + timedelta(minutes=i)
            records.append({
                'date': record_time.date(),
                'start_time': record_time,
                'end_time': record_time + timedelta(minutes=10),
                'duration': 10,
                'card_name': f'テストカード{i % 5}',
                'notes': f'テストメモ{i}'
            })
        
        # 一括挿入
        with db.atomic():
            MeditationRecord.insert_many(records).execute()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 1秒以内に完了することを期待
        assert duration < 1.0, f"Bulk insert took {duration:.2f} seconds"

def test_database_query_performance(test_db_path):
    """データベースクエリのパフォーマンステスト"""
    with database_connection(test_db_path):
        # テストデータの準備
        base_time = datetime.now()
        records = []
        for i in range(1000):
            record_time = base_time + timedelta(minutes=i)
            records.append({
                'date': record_time.date(),
                'start_time': record_time,
                'end_time': record_time + timedelta(minutes=10),
                'duration': 10,
                'card_name': f'テストカード{i % 5}',
                'notes': f'テストメモ{i}'
            })
        
        with db.atomic():
            MeditationRecord.insert_many(records).execute()
        
        # クエリのパフォーマンス測定
        start_time = time.time()
        
        # 複数の複雑なクエリを実行
        queries = [
            # 日付範囲での検索
            MeditationRecord.select().where(
                MeditationRecord.date.between(
                    base_time.date(),
                    (base_time + timedelta(days=7)).date()
                )
            ),
            
            # カード名での検索とソート
            MeditationRecord.select().where(
                MeditationRecord.card_name.contains('カード')
            ).order_by(MeditationRecord.start_time.desc()),
            
            # 集計クエリ
            MeditationRecord.select(
                MeditationRecord.card_name,
                db.fn.AVG(MeditationRecord.duration).alias('avg_duration')
            ).group_by(MeditationRecord.card_name)
        ]
        
        # すべてのクエリを実行
        for query in queries:
            list(query)  # クエリを実行して結果をリストに変換
        
        end_time = time.time()
        duration = end_time - start_time
        
        # すべてのクエリが0.5秒以内に完了することを期待
        assert duration < 0.5, f"Queries took {duration:.2f} seconds"

@pytest.mark.skip(reason="長時間実行のため通常のテストでは実行しない")
def test_long_term_stability(test_db_path):
    """長時間安定性テスト"""
    with database_connection(test_db_path):
        start_time = time.time()
        end_time = start_time + 3600  # 1時間実行
        
        while time.time() < end_time:
            # データの作成
            record = MeditationRecord.create(
                date=datetime.now().date(),
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(minutes=10),
                duration=10,
                card_name='テストカード',
                notes='テストメモ'
            )
            
            # データの読み取り
            retrieved = MeditationRecord.get_by_id(record.id)
            assert retrieved is not None
            
            # データの更新
            retrieved.notes = '更新されたメモ'
            retrieved.save()
            
            # データの削除
            retrieved.delete_instance()
            
            # 短い待機
            time.sleep(1)
        
        # エラーなく完了することを確認
        assert True, "Long-term stability test completed successfully"
