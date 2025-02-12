# TattvaVision 今後の開発計画

## ✅ 完了済みの機能

### データ保護とバックアップ 🔒
- **手動バックアップ**
  - ✅ 設定画面からのデータベースバックアップとリストア機能
  - ✅ バックアップファイルの保存場所とファイル名を任意選択可能
  - ✅ バックアップ履歴の管理（最終バックアップ日時の記録）
  - ✅ エラーログ記録機能

### データインポート/エクスポート機能
- **CSVサポート**
  - ✅ エクスポート・インポート機能
  - ✅ 日付形式オプション対応
  - ✅ 設定画面からのアクセス

## 1. エラーハンドリングの強化 🛠️

### データベース関連
- ✅ データベース操作時の基本的なエラーハンドリング
  - ✅ 保存・読み込み時のエラーメッセージ表示
  - ✅ データベース接続エラーの通知
  - ✅ リカバリーメカニズムの実装（バックアップ/復元）

### ファイル操作
- **画像ファイル**
  - ✅ PNG形式のみのサポート
  - ✅ 201x257ピクセルサイズの固定
  - ✅ `[element1]_[element2].png`の命名規則
  - エラー時のユーザーフレンドリーな通知
    - 画像が見つからない場合
    - サイズが異なる場合
    - 形式が異なる場合
  - 画像の整合性チェック（破損ファイルの検出）
  - 新規画像追加時の自動バリデーション

**優先度: 高**  
📝 *注釈: 現状は基本的なエラーハンドリングのみ。本番運用を見据えて強化が必要。特にデータベース操作周りは重点的に。*

## 2. ドキュメント整備 📚

### ユーザードキュメント
- `docs/USER_GUIDE.md`
  - インストール手順
  - 基本的な使い方
  - 詳細機能の説明
  - トラブルシューティング
  - よくある質問

### 開発者ドキュメント
- `docs/DEVELOPER_GUIDE.md`
  - プロジェクト概要
  - アーキテクチャ説明
  - 開発環境のセットアップ
  - コーディング規約
  - テスト方法
  - デプロイメント手順
  - 貢献ガイドライン

**優先度: 中**  
📝 *注釈: ドキュメントは定期的に更新し、最新の状態を維持する必要があります。*

## 3. GUIテストの改善と制限事項 🧪

### 既知の問題
- **設定ウィンドウのテスト制限**
  - `test_settings_window.py`の`test_settings_window_components`でフリーズ発生
  - ヘッドレスモード（QT_QPA_PLATFORM=minimal）でも解決せず
  - モーダルウィンドウの表示・非表示操作に関する問題

### 対応方針
- **代替テスト戦略**
  - ユニットテストレベルでのコンポーネント検証
  - モックを活用したイベントハンドリングのテスト
  - 重要な機能のE2Eテストは手動テストで補完

### 今後の改善案
- コンポーネントの分離とテスタビリティの向上
- テスト用の特別なウィンドウモードの実装
- CIでのGUIテスト実行方法の最適化

**優先度: 中**  
📝 *注釈: 現状の制限を認識しつつ、段階的にテストカバレッジを向上させる。特に重要な機能から優先的に対応する。*

## 4. 国際化対応の拡充 🌐

### 多言語サポート
- **基本言語サポート**
  - 日本語（ja）と英語（en）の標準サポート
  - 専用の言語ファイルフォルダを作成
  - カスタム言語ファイルのサポート（ユーザーによる追加可能）

### ユーザーフィードバック
- 一般ユーザー向けの分かりやすいエラーメッセージ
- よくあるエラーに対する解決方法のガイダンス
- トラブルシューティングのヘルプドキュメント

**優先度: 低**  
📝 *注釈: 基本的な多言語サポートは実装済み。追加言語のサポートは需要に応じて対応。*

## 4. テストの強化 🧪

### GUI テスト
- テストの安定性向上
  - 非同期処理の待機時間調整
  - テスト環境の一貫性確保
- クロスプラットフォームテスト
  - Windows以外のOSでのテスト実行
  - 画面解像度の違いによる影響確認

### ユニットテスト
- カバレッジの向上
  - 未テストのコンポーネントの特定
  - テストケースの追加
- エッジケースのテスト
  - 異常値の入力
  - 境界値のテスト

**優先度: 中**  
📝 *注釈: テストの安定性が課題。特にGUIテストは環境依存の問題が多い。*

## 実装の優先順位 📋

1. エラーハンドリングの強化
2. ドキュメント整備
3. GUIテストの改善
4. 国際化対応の拡充
5. テストの強化

## 注意事項 ⚠️

- 各機能の実装前に、ユーザーフィードバックを得ることが望ましい
- バックアップ機能は早急に実装すべき
- テスト環境の整備も並行して進める必要あり
- GitHubのIssueで進捗管理を行うことを推奨
