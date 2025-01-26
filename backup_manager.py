import json
import shutil
import sqlite3
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
from settings import settings
from i18n import i18n

# ロガーの設定
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('backup_manager')

class BackupManager:
    def __init__(self):
        self.db_path = Path('meditation.db')
        self.backup_dir = settings.backup_dir
        self._ensure_backup_dir()

    def _ensure_backup_dir(self):
        """バックアップディレクトリが存在することを確認"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)

    def create_backup(self, custom_path: Optional[Path] = None) -> tuple[bool, str]:
        """
        データベースのバックアップを作成
        
        Args:
            custom_path: カスタムバックアップパス（オプション）
        
        Returns:
            (成功したかどうか, メッセージ)
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = custom_path or (self.backup_dir / f'meditation_backup_{timestamp}.db')
            
            # データベースをコピー
            shutil.copy2(self.db_path, backup_path)
            
            # 最終バックアップ時刻を更新
            settings.last_backup = timestamp
            
            logger.info(f'Backup created successfully at {backup_path}')
            return True, i18n.get('backup.success')
            
        except Exception as e:
            logger.error(f'Backup creation failed: {str(e)}')
            return False, f"{i18n.get('backup.error')}: {str(e)}"

    def restore_backup(self, backup_path: Path) -> tuple[bool, str]:
        """
        バックアップからデータベースを復元
        
        Args:
            backup_path: 復元するバックアップファイルのパス
        
        Returns:
            (成功したかどうか, メッセージ)
        """
        try:
            if not backup_path.exists():
                raise FileNotFoundError(i18n.get('error.file_not_found'))
            
            # 現在のDBをテンポラリバックアップ
            temp_backup = self.db_path.with_suffix('.db.temp')
            shutil.copy2(self.db_path, temp_backup)
            
            try:
                # バックアップから復元
                shutil.copy2(backup_path, self.db_path)
                temp_backup.unlink()  # テンポラリバックアップを削除
                
                logger.info(f'Database restored from {backup_path}')
                return True, i18n.get('backup.restore_success')
                
            except Exception as e:
                # 復元に失敗した場合、テンポラリバックアップから戻す
                if temp_backup.exists():
                    shutil.copy2(temp_backup, self.db_path)
                    temp_backup.unlink()
                raise e
                
        except Exception as e:
            logger.error(f'Restore failed: {str(e)}')
            return False, f"{i18n.get('backup.restore_error')}: {str(e)}"

    def export_csv(self, export_path: Path, date_format: str = 'yyyy-mm-dd') -> tuple[bool, str]:
        """
        データベースの内容をCSVにエクスポート
        
        Args:
            export_path: エクスポート先のパス
            date_format: 日付フォーマット ('yyyy-mm-dd' or 'yyyy/mm/dd')
        
        Returns:
            (成功したかどうか, メッセージ)
        """
        try:
            date_format_sql = '%Y-%m-%d' if date_format == 'yyyy-mm-dd' else '%Y/%m/%d'
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # meditation_recordsテーブルからデータを取得
                cursor.execute(f"""
                    SELECT id, 
                           strftime('{date_format_sql}', date) as formatted_date,
                           card_name,
                           meditation_time,
                           notes
                    FROM meditation_records
                    ORDER BY date
                """)
                
                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'Date', 'Card Name', 'Meditation Time', 'Notes'])
                    writer.writerows(cursor.fetchall())
            
            logger.info(f'CSV exported successfully to {export_path}')
            return True, i18n.get('csv.export_success')
            
        except Exception as e:
            logger.error(f'CSV export failed: {str(e)}')
            return False, f"{i18n.get('csv.export_error')}: {str(e)}"

    def import_csv(self, import_path: Path, date_format: str = 'yyyy-mm-dd') -> tuple[bool, str]:
        """
        CSVからデータベースにインポート
        
        Args:
            import_path: インポートするCSVファイルのパス
            date_format: CSVの日付フォーマット ('yyyy-mm-dd' or 'yyyy/mm/dd')
        
        Returns:
            (成功したかどうか, メッセージ)
        """
        try:
            if not import_path.exists():
                raise FileNotFoundError(i18n.get('error.file_not_found'))
            
            # テンポラリバックアップを作成
            success, msg = self.create_backup()
            if not success:
                raise Exception(f"Backup failed before import: {msg}")
            
            date_format_py = '%Y-%m-%d' if date_format == 'yyyy-mm-dd' else '%Y/%m/%d'
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                with open(import_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # 日付を解析してSQLite形式に変換
                        date_obj = datetime.strptime(row['Date'], date_format_py)
                        sqlite_date = date_obj.strftime('%Y-%m-%d')
                        
                        cursor.execute("""
                            INSERT INTO meditation_records (date, card_name, meditation_time, notes)
                            VALUES (?, ?, ?, ?)
                        """, (sqlite_date, row['Card Name'], row['Meditation Time'], row['Notes']))
                
                conn.commit()
            
            logger.info(f'CSV imported successfully from {import_path}')
            return True, i18n.get('csv.import_success')
            
        except Exception as e:
            logger.error(f'CSV import failed: {str(e)}')
            return False, f"{i18n.get('csv.import_error')}: {str(e)}"

# グローバルなBackupManagerインスタンス
backup_manager = BackupManager()
