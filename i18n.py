import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from settings import settings

class I18n:
    def __init__(self):
        self._translations: Dict[str, Dict[str, Any]] = {}
        self._load_translations()

    def _load_translations(self):
        """利用可能な全ての言語ファイルを読み込む"""
        locales_dir = settings.locales_dir
        if not locales_dir.exists():
            return

        for file in locales_dir.glob('*.json'):
            lang = file.stem
            with open(file, 'r', encoding='utf-8') as f:
                self._translations[lang] = json.load(f)

    def get(self, key: str, lang: Optional[str] = None) -> str:
        """
        指定されたキーの翻訳を取得する
        
        Args:
            key: ドット区切りの翻訳キー (例: "app.title")
            lang: 言語コード (指定がない場合は現在の設定言語を使用)
        
        Returns:
            翻訳されたテキスト。翻訳が見つからない場合はキーをそのまま返す
        """
        if lang is None:
            lang = settings.language

        if lang not in self._translations:
            return key

        current = self._translations[lang]
        for part in key.split('.'):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return key

        return current if isinstance(current, str) else key

    def available_languages(self) -> list[str]:
        """利用可能な言語のリストを返す"""
        return list(self._translations.keys())

# グローバルなI18nインスタンス
i18n = I18n()
