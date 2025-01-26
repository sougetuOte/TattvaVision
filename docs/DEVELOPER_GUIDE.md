# TattvaVision 開発者ガイド

## 目次
1. [プロジェクト概要](#プロジェクト概要)
2. [アーキテクチャ](#アーキテクチャ)
3. [開発環境のセットアップ](#開発環境のセットアップ)
4. [コーディング規約](#コーディング規約)
5. [テスト](#テスト)
6. [デプロイメント](#デプロイメント)
7. [貢献ガイドライン](#貢献ガイドライン)

## プロジェクト概要

### 技術スタック
- **フレームワーク**: PySide6 (Qt for Python)
- **データベース**: SQLite (peewee ORM)
- **その他の主要ライブラリ**:
  - pandas: データ処理
  - Pillow: 画像処理
  - pydub: 音声処理

### プロジェクト構造
```
TattvaVision/
├── docs/                    # ドキュメント
├── images/                  # タットワカード画像
├── locales/                 # 言語ファイル
├── sounds/                  # 音声ファイル
├── backups/                 # バックアップファイル
├── tattva_app.py           # メインアプリケーション
├── database.py             # データベース定義
├── record_window.py        # 記録一覧ウィンドウ
├── settings_window.py      # 設定ウィンドウ
├── i18n.py                 # 国際化
├── backup_manager.py       # バックアップ管理
├── settings.py             # 設定管理
├── requirements.txt        # 依存パッケージ
└── README.md               # プロジェクト概要
```

## アーキテクチャ

### コンポーネント構成
1. **GUI層**
   - `TattvaApp`: メインウィンドウ
   - `RecordWindow`: 記録一覧
   - `SettingsWindow`: 設定画面

2. **ビジネスロジック層**
   - `BackupManager`: バックアップ処理
   - `I18n`: 国際化
   - `Settings`: 設定管理

3. **データ層**
   - `database.py`: ORMモデル定義
   - `MeditationRecord`: 瞑想記録モデル

### データフロー
1. ユーザーインタラクション
2. GUIイベントハンドリング
3. ビジネスロジック処理
4. データベース操作
5. UI更新

## 開発環境のセットアップ

### 必要なツール
- Python 3.8以上
- Git
- Visual Studio Code（推奨）

### セットアップ手順
1. リポジトリのクローン
   ```bash
   git clone [repository-url]
   cd TattvaVision
   ```

2. 仮想環境の作成
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. 依存パッケージのインストール
   ```bash
   pip install -r requirements.txt
   ```

## コーディング規約

### Pythonコーディング規約
- PEP 8に準拠
- インデント: 4スペース
- 最大行長: 100文字
- ドキュメンテーション: Google Style Python Docstrings

### 命名規則
- クラス名: UpperCamelCase
- メソッド名: snake_case
- 変数名: snake_case
- 定数: UPPER_SNAKE_CASE

### コメント規則
- クラス、メソッドには必ずドキュメンテーションコメントを付ける
- 複雑なロジックには説明コメントを付ける
- TODO、FIXME、NOTEなどのタグを適切に使用

## テスト

### テストフレームワーク
- unittest: 単体テスト
- pytest: 統合テスト

### テスト構造
```
tests/
├── unit/                   # 単体テスト
│   ├── test_database.py
│   ├── test_i18n.py
│   └── test_backup.py
└── integration/           # 統合テスト
    ├── test_gui.py
    └── test_workflow.py
```

### テスト実行
```bash
# 全テストの実行
python -m pytest

# 特定のテストの実行
python -m pytest tests/unit/test_database.py
```

## デプロイメント

### ビルド手順
1. バージョン番号の更新
2. 依存パッケージの確認
3. テストの実行
4. 実行ファイルの生成
   ```bash
   pyinstaller --onefile tattva_app.py
   ```

### リリースチェックリスト
- [ ] すべてのテストが成功
- [ ] バージョン番号が更新
- [ ] CHANGELOGが更新
- [ ] ドキュメントが最新
- [ ] 必要なアセットが同梱

## 貢献ガイドライン

### プルリクエストの手順
1. 新しいブランチを作成
2. 変更を実装
3. テストを追加/更新
4. プルリクエストを作成

### コミットメッセージの規約
- feat: 新機能
- fix: バグ修正
- docs: ドキュメントのみの変更
- style: コードスタイルの変更
- refactor: リファクタリング
- test: テストの追加/修正
- chore: ビルドプロセスやツールの変更

### レビュープロセス
1. コードレビュー
2. テストの確認
3. ドキュメントの確認
4. マージ承認
