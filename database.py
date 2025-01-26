from datetime import datetime
import os
import shutil
from peewee import *
from PySide6.QtWidgets import QMessageBox

# データベースのパス設定
DB_PATH = 'meditation.db'
BACKUP_PATH = 'meditation.db.bak'

# データベース接続
db = SqliteDatabase(None)

class BaseModel(Model):
    class Meta:
        database = db

class MeditationRecord(BaseModel):
    id = AutoField()
    date = DateField()
    start_time = DateTimeField()
    end_time = DateTimeField()
    duration = IntegerField()  # 分単位
    card_name = CharField()
    notes = TextField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        """保存時に更新日時を設定"""
        self.updated_at = datetime.now()
        return super(MeditationRecord, self).save(*args, **kwargs)

    def get_duration_status(self):
        """瞑想時間に基づくステータスを返す"""
        if self.duration < 10:
            return "短時間瞑想"
        elif self.duration < 20:
            return "通常瞑想"
        else:
            return "長時間瞑想"

    def get_element(self):
        """カード名から元素を抽出する"""
        element_mapping = {
            "地": "地",
            "水": "水",
            "火": "火",
            "風": "風",
            "空": "空"
        }
        
        for element in element_mapping:
            if element in self.card_name:
                return element_mapping[element]
        return "不明"

    def extract_keywords(self):
        """瞑想メモからキーワードを抽出する"""
        keywords = []
        important_words = ["平和", "集中", "安定", "エネルギー", "気づき", "調和", "落ち着き"]
        
        for word in important_words:
            if word in self.notes:
                keywords.append(word)
        
        return keywords

def backup_database():
    """データベースのバックアップを作成"""
    try:
        if os.path.exists(DB_PATH):
            shutil.copy2(DB_PATH, BACKUP_PATH)
    except Exception as e:
        print(f"バックアップ作成エラー: {str(e)}")

def restore_from_backup():
    """バックアップからデータベースを復元"""
    try:
        if os.path.exists(BACKUP_PATH):
            shutil.copy2(BACKUP_PATH, DB_PATH)
            return True
    except Exception as e:
        print(f"バックアップ復元エラー: {str(e)}")
    return False

def initialize_database():
    """データベースの初期化"""
    db_exists = os.path.exists(DB_PATH)
    backup_exists = os.path.exists(BACKUP_PATH)

    if not db_exists:
        if backup_exists:
            # バックアップから復元を試みる
            if restore_from_backup():
                QMessageBox.information(
                    None,
                    "データベース復元",
                    "データベースファイルが見つかりませんでした。\nバックアップから復元しました。"
                )
            else:
                QMessageBox.warning(
                    None,
                    "データベース作成",
                    "データベースファイルとバックアップが見つかりませんでした。\n新しいデータベースを作成します。"
                )
        else:
            QMessageBox.warning(
                None,
                "データベース作成",
                "データベースファイルが見つかりませんでした。\n新しいデータベースを作成します。"
            )

    # データベースの接続と初期化
    db.init(DB_PATH)
    db.connect()
    db.create_tables([MeditationRecord], safe=True)
    db.close()

    # 正常に初期化できた場合はバックアップを作成
    if not backup_exists:
        backup_database()
