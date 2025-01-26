# TattvaVision

タットワ瞑想の実践と記録をサポートするデスクトップアプリケーション

## 概要

TattvaVisionは、タットワ瞑想の実践者のために開発された専用のデスクトップアプリケーションです。タットワカードの表示、瞑想タイマー、記録管理などの機能を提供し、継続的な瞑想実践をサポートします。

## 主な機能

- タットワカードの表示と解釈
- カスタマイズ可能な瞑想タイマー
- 瞑想記録の保存と管理
- 記録の検索とエクスポート機能

## インストール

1. Pythonのインストール（3.8以上を推奨）
2. 必要なパッケージのインストール:
```bash
pip install -r requirements.txt
```

## 使用方法

1. アプリケーションの起動:
```bash
python tattva_app.py
```

2. カードの選択:
   - ドロップダウンメニューから目的のカードを選択
   - カードの画像と解釈が表示されます

3. 瞑想の開始:
   - 希望する瞑想時間を設定
   - 「開始」ボタンをクリック
   - 5秒のカウントダウン後に瞑想が始まります

4. 記録の保存:
   - 瞑想終了後、気づきや感想をメモ
   - 「記録を保存」をクリックして保存
   - 「記録一覧」から過去の記録を確認可能

## 必要システム要件

- Windows 10以上
- Python 3.8以上
- 画面解像度 1000x600 以上

## 依存パッケージ

- PySide6
- pandas
- peewee
- Pillow
- pydub

## クレジット

### 音声ファイル
- 瞑想開始音: ["Copper Bell Ding"](https://pixabay.com/sound-effects/copper-bell-ding-25-204990/)
  - 提供: Pixabay Sound Library
  - ライセンス: Pixabay License（商用利用可、クレジット表記不要）
- 瞑想終了音: ["Singing Bowl Hit"](https://pixabay.com/sound-effects/singing-bowl-hit-3-33366/)
  - 提供: Pixabay Sound Library
  - ライセンス: Pixabay License（商用利用可、クレジット表記不要）

## ライセンス

[MIT License](LICENSE)

## 作者

- sougetuOte (metral@sougetu.net)

## 貢献

バグ報告や機能改善の提案は、GitHubのIssueやPull Requestsを通じてお願いします。
