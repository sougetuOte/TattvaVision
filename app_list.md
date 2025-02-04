# アプリケーションファイル構成リスト

このファイルは、exe化および配布に必要なファイルとディレクトリ構成をまとめたものです。

## 1. メインプログラムとPythonファイル

- `tattva_app.py`: アプリケーションのエントリーポイント。exe化の際にメインファイルとして利用されます。
- 関連するその他のPythonファイル: 
  - `*.py` ファイル群（ライブラリ、モジュール、ヘルパースクリプトなど）
    - これらは `tattva_app.py` と連携して動作するため、exe作成時に同梱が必要です。

## 2. リソースディレクトリとファイル

- **@[images]**: 画像ファイルを格納するディレクトリ
  - 例: `c:\work3\TattvaVision\images`

- **@[locales]**: ローカライズファイル（多言語対応用のテキスト、設定ファイル等）
  - 例: `c:\work3\TattvaVision\locales`

- **@[sounds]**: サウンドファイル（効果音、BGM 等）
  - 例: `c:\work3\TattvaVision\sounds`

- **@[tattva.csv]**: CSV形式のデータファイル。アプリの動作に必要なデータが含まれる可能性があります
  - 例: `c:\work3\TattvaVision\tattva.csv`

## 3. その他推奨ファイル

- `README.md`: プロジェクトの概要、インストール手順、使用法などのドキュメント。
- `LICENSE`: ライセンス情報（必要に応じて）。
- `requirements.txt`: インストールするPythonパッケージの一覧（もし存在すれば）。

## 4. ディレクトリ構成例

```
TattvaVision/
├── tattva_app.py         # メインファイル
├── other_module.py       # その他のPythonファイル（例）
├── images/               # 画像ファイル群
├── locales/              # ローカリゼーションファイル
├── sounds/               # サウンド関連ファイル
├── tattva.csv            # CSVデータファイル
├── README.md             # プロジェクト概要
├── LICENSE               # ライセンス情報
└── requirements.txt      # Python依存パッケージ（存在する場合）
```

## 5. exe化および配布手順との関係

上記のファイルとディレクトリは、exe作成ツール（例：PyInstaller）でのexeビルド時に、必要に応じて`--add-data`オプションを利用して一緒にパッケージする必要があります。

また、exeビルド後には、生成されたexeファイル（通常は `dist/` フォルダに出力される）と上記のリソース群を1つのフォルダに集約し、zip形式に圧縮して配布する形としてください。

## 6. PyInstaller コマンド例

以下は、全ての必要ファイルおよび推奨ファイルを含めた PyInstaller コマンドの例です:

```
pyinstaller --onefile ^
  --add-data "images;images" ^
  --add-data "locales;locales" ^
  --add-data "sounds;sounds" ^
  --add-data "tattva.csv;." ^
  tattva_app.py
```

各 `--add-data` オプションは、Python プログラムの実行に必要なリソースを exe に同梱するためのものです。Windows環境では、ファイルパスの区切りにセミコロン (;) を使用してください。
