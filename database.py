from datetime import datetime
from peewee import *

# データベースの設定
db = SqliteDatabase('meditation.db')

class BaseModel(Model):
    class Meta:
        database = db

class MeditationRecord(BaseModel):
    date = DateTimeField(default=datetime.now)
    start_time = DateTimeField()
    end_time = DateTimeField()
    duration = IntegerField()  # 分単位
    card_name = CharField()
    notes = TextField(null=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(MeditationRecord, self).save(*args, **kwargs)

def initialize_database():
    """データベースの初期化"""
    db.connect()
    db.create_tables([MeditationRecord], safe=True)
    db.close()
