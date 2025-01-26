import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

class Settings:
    def __init__(self):
        self.app_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.settings_file = self.app_dir / 'settings.json'
        self.locales_dir = self.app_dir / 'locales'
        self.backups_dir = self.app_dir / 'backups'
        self._settings = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        """設定ファイルを読み込む"""
        if self.settings_file.exists():
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'language': 'ja',
            'date_format': 'yyyy-mm-dd',
            'backup_dir': str(self.backups_dir),
            'last_backup': None
        }

    def save_settings(self):
        """設定をファイルに保存"""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self._settings, f, ensure_ascii=False, indent=2)

    @property
    def language(self) -> str:
        return self._settings.get('language', 'ja')

    @language.setter
    def language(self, value: str):
        self._settings['language'] = value
        self.save_settings()

    @property
    def date_format(self) -> str:
        return self._settings.get('date_format', 'yyyy-mm-dd')

    @date_format.setter
    def date_format(self, value: str):
        self._settings['date_format'] = value
        self.save_settings()

    @property
    def backup_dir(self) -> Path:
        return Path(self._settings.get('backup_dir', str(self.backups_dir)))

    @backup_dir.setter
    def backup_dir(self, value: str):
        self._settings['backup_dir'] = str(value)
        self.save_settings()

    @property
    def last_backup(self) -> Optional[str]:
        return self._settings.get('last_backup')

    @last_backup.setter
    def last_backup(self, value: Optional[str]):
        self._settings['last_backup'] = value
        self.save_settings()

# グローバルなSettings インスタンス
settings = Settings()
