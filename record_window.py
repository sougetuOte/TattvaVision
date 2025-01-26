from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QTableWidget, QTableWidgetItem, QLabel,
                               QLineEdit, QDialog, QTextEdit, QMessageBox, QFileDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from database import MeditationRecord, db
from datetime import datetime
import csv
import codecs

class EditDialog(QDialog):
    def __init__(self, record, parent=None):
        super().__init__(parent)
        self.record = record
        self.setWindowTitle("記録の編集")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 情報表示
        info_text = (
            f"日時: {self.record.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"開始時刻: {self.record.start_time.strftime('%H:%M:%S')}\n"
            f"終了時刻: {self.record.end_time.strftime('%H:%M:%S')}\n"
            f"瞑想時間: {self.record.duration}分\n"
            f"選択したカード: {self.record.card_name}\n"
        )
        info_label = QLabel(info_text)
        layout.addWidget(info_label)
        
        # メモ編集エリア
        layout.addWidget(QLabel("瞑想記録:"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setText(self.record.notes or "")
        layout.addWidget(self.notes_edit)
        
        # ボタン
        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_record)
        delete_button = QPushButton("削除")
        delete_button.clicked.connect(self.delete_record)
        cancel_button = QPushButton("キャンセル")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def save_record(self):
        try:
            with db.atomic():
                self.record.notes = self.notes_edit.toPlainText()
                self.record.save()
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"保存に失敗しました: {str(e)}")

    def delete_record(self):
        reply = QMessageBox.question(
            self, "確認", "この記録を削除してもよろしいですか？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with db.atomic():
                    self.record.delete_instance()
                self.accept()
            except Exception as e:
                QMessageBox.warning(self, "エラー", f"削除に失敗しました: {str(e)}")

class DeleteConfirmationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚠️ 警告: データの完全削除")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 警告メッセージ
        warning_label = QLabel("⚠️ 全ての瞑想記録を削除しようとしています！")
        warning_label.setStyleSheet("QLabel { color: red; font-weight: bold; font-size: 14px; }")
        layout.addWidget(warning_label)
        
        # 詳細説明
        detail_label = QLabel(
            "この操作は取り消すことができません。\n"
            "続行する前に、必要なデータをエクスポートすることを推奨します。\n\n"
            "本当に全ての記録を削除しますか？"
        )
        detail_label.setWordWrap(True)
        layout.addWidget(detail_label)
        
        # ボタン
        button_layout = QHBoxLayout()
        delete_button = QPushButton("削除")
        delete_button.setStyleSheet("QPushButton { background-color: red; color: white; font-weight: bold; }")
        delete_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("キャンセル")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(delete_button)
        layout.addLayout(button_layout)

class RecordWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("瞑想記録一覧")
        self.setGeometry(150, 150, 800, 600)
        self.setup_ui()
        self.load_records()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 検索バー
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("記録を検索...")
        self.search_input.textChanged.connect(self.load_records)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # テーブル
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "日付", "開始時刻", "終了時刻", "瞑想時間", "カード", "記録"
        ])
        self.table.itemDoubleClicked.connect(self.edit_record)
        layout.addWidget(self.table)
        
        # ヘッダーのクリックでソート可能に
        self.table.horizontalHeader().setSectionsClickable(True)
        self.table.horizontalHeader().sectionClicked.connect(self.sort_table)
        
        # ボタンレイアウト
        button_layout = QHBoxLayout()
        
        # 更新ボタン
        refresh_button = QPushButton("更新")
        refresh_button.clicked.connect(self.load_records)
        button_layout.addWidget(refresh_button)
        
        # エクスポートボタン
        export_button = QPushButton("📊 CSVエクスポート")
        export_button.clicked.connect(self.export_records)
        button_layout.addWidget(export_button)
        
        # 削除ボタン
        delete_all_button = QPushButton("🗑️ 全データ削除")
        delete_all_button.setStyleSheet("QPushButton { color: red; }")
        delete_all_button.clicked.connect(self.delete_all_records)
        button_layout.addWidget(delete_all_button)
        
        layout.addLayout(button_layout)

    def export_records(self):
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "エクスポート先を選択",
                f"meditation_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if file_name:
                with codecs.open(file_name, 'w', 'utf-8-sig') as f:
                    writer = csv.writer(f)
                    # ヘッダー（日本語と英語）
                    writer.writerow([
                        '日付/Date', '開始時刻/Start Time', '終了時刻/End Time',
                        '瞑想時間(分)/Duration(min)', 'カード/Card', '記録/Notes'
                    ])
                    
                    records = MeditationRecord.select().order_by(MeditationRecord.date.desc())
                    for record in records:
                        writer.writerow([
                            record.date.strftime('%Y-%m-%d %H:%M:%S'),
                            record.start_time.strftime('%H:%M:%S'),
                            record.end_time.strftime('%H:%M:%S'),
                            record.duration,
                            record.card_name,
                            record.notes or ''
                        ])
                
                QMessageBox.information(self, "成功", "データを正常にエクスポートしました。")
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"エクスポート中にエラーが発生しました: {str(e)}")

    def delete_all_records(self):
        dialog = DeleteConfirmationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                with db.atomic():
                    MeditationRecord.delete().execute()
                self.load_records()
                QMessageBox.information(self, "成功", "全ての記録を削除しました。")
            except Exception as e:
                QMessageBox.warning(self, "エラー", f"削除中にエラーが発生しました: {str(e)}")

    def load_records(self):
        search_text = self.search_input.text().strip()
        
        # 検索クエリの構築
        query = MeditationRecord.select()
        if search_text:
            query = query.where(MeditationRecord.notes.contains(search_text))
        
        # レコードの取得と表示
        records = list(query.order_by(MeditationRecord.date.desc()))
        self.table.setRowCount(len(records))
        
        for i, record in enumerate(records):
            self.table.setItem(i, 0, QTableWidgetItem(record.date.strftime('%Y-%m-%d')))
            self.table.setItem(i, 1, QTableWidgetItem(record.start_time.strftime('%H:%M:%S')))
            self.table.setItem(i, 2, QTableWidgetItem(record.end_time.strftime('%H:%M:%S')))
            self.table.setItem(i, 3, QTableWidgetItem(f"{record.duration}分"))
            self.table.setItem(i, 4, QTableWidgetItem(record.card_name))
            self.table.setItem(i, 5, QTableWidgetItem(record.notes[:50] + "..." if record.notes and len(record.notes) > 50 else record.notes or ""))
            
            # レコードIDを非表示データとして保存
            self.table.item(i, 0).setData(Qt.UserRole, record.id)
        
        self.table.resizeColumnsToContents()

    def edit_record(self, item):
        record_id = self.table.item(item.row(), 0).data(Qt.UserRole)
        record = MeditationRecord.get_by_id(record_id)
        
        dialog = EditDialog(record, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_records()

    def sort_table(self, column):
        self.table.sortItems(column)

    def closeEvent(self, event):
        db.close()
        event.accept()
