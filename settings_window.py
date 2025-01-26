from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QComboBox, QFileDialog, QMessageBox, QGroupBox)
from PySide6.QtCore import Qt
from pathlib import Path
from settings import settings
from i18n import i18n
from backup_manager import backup_manager

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(i18n.get('app.settings'))
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 言語設定
        lang_group = QGroupBox(i18n.get('app.language'))
        lang_layout = QVBoxLayout()
        self.lang_combo = QComboBox()
        for lang in i18n.available_languages():
            self.lang_combo.addItem(lang.upper(), lang)
        current_index = self.lang_combo.findData(settings.language)
        if current_index >= 0:
            self.lang_combo.setCurrentIndex(current_index)
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(self.lang_combo)
        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)

        # 日付形式設定
        date_group = QGroupBox(i18n.get('app.date_format'))
        date_layout = QVBoxLayout()
        self.date_combo = QComboBox()
        self.date_combo.addItem("YYYY-MM-DD", "yyyy-mm-dd")
        self.date_combo.addItem("YYYY/MM/DD", "yyyy/mm/dd")
        current_index = self.date_combo.findData(settings.date_format)
        if current_index >= 0:
            self.date_combo.setCurrentIndex(current_index)
        self.date_combo.currentIndexChanged.connect(self.change_date_format)
        date_layout.addWidget(self.date_combo)
        date_group.setLayout(date_layout)
        layout.addWidget(date_group)

        # バックアップ設定
        backup_group = QGroupBox(i18n.get('app.backup'))
        backup_layout = QVBoxLayout()

        # バックアップディレクトリ
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel(str(settings.backup_dir))
        dir_layout.addWidget(self.dir_label)
        dir_button = QPushButton(i18n.get('backup.select_dir'))
        dir_button.clicked.connect(self.select_backup_dir)
        dir_layout.addWidget(dir_button)
        backup_layout.addLayout(dir_layout)

        # バックアップ操作ボタン
        backup_buttons = QHBoxLayout()
        create_backup = QPushButton(i18n.get('backup.create'))
        create_backup.clicked.connect(self.create_backup)
        restore_backup = QPushButton(i18n.get('backup.restore'))
        restore_backup.clicked.connect(self.restore_backup)
        backup_buttons.addWidget(create_backup)
        backup_buttons.addWidget(restore_backup)
        backup_layout.addLayout(backup_buttons)

        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)

        # CSV操作
        csv_group = QGroupBox("CSV")
        csv_layout = QVBoxLayout()
        csv_buttons = QHBoxLayout()
        
        export_csv = QPushButton(i18n.get('csv.export'))
        export_csv.clicked.connect(self.export_csv)
        import_csv = QPushButton(i18n.get('csv.import'))
        import_csv.clicked.connect(self.import_csv)
        
        csv_buttons.addWidget(export_csv)
        csv_buttons.addWidget(import_csv)
        csv_layout.addLayout(csv_buttons)
        
        csv_group.setLayout(csv_layout)
        layout.addWidget(csv_group)

        # 閉じるボタン
        close_button = QPushButton("OK")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

    def change_language(self, index):
        lang = self.lang_combo.itemData(index)
        if lang != settings.language:
            settings.language = lang
            QMessageBox.information(
                self,
                i18n.get('app.settings'),
                "言語設定を変更しました。\nLanguage settings have been changed.\n変更を適用するにはアプリケーションを再起動してください。\nPlease restart the application to apply changes."
            )

    def change_date_format(self, index):
        date_format = self.date_combo.itemData(index)
        if date_format != settings.date_format:
            settings.date_format = date_format

    def select_backup_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            i18n.get('backup.select_dir'),
            str(settings.backup_dir)
        )
        if dir_path:
            settings.backup_dir = dir_path
            self.dir_label.setText(dir_path)

    def create_backup(self):
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                i18n.get('backup.select_file'),
                str(settings.backup_dir / f"meditation_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"),
                "Database Files (*.db)"
            )
            if file_name:
                success, message = backup_manager.create_backup(Path(file_name))
                if success:
                    QMessageBox.information(self, i18n.get('app.backup'), message)
                else:
                    QMessageBox.warning(self, i18n.get('app.backup'), message)
        except Exception as e:
            QMessageBox.warning(self, i18n.get('app.backup'), str(e))

    def restore_backup(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                i18n.get('backup.select_file'),
                str(settings.backup_dir),
                "Database Files (*.db)"
            )
            if file_name:
                reply = QMessageBox.question(
                    self,
                    i18n.get('app.backup'),
                    "現在のデータベースは上書きされます。続行しますか？\nCurrent database will be overwritten. Continue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    success, message = backup_manager.restore_backup(Path(file_name))
                    if success:
                        QMessageBox.information(self, i18n.get('app.backup'), message)
                    else:
                        QMessageBox.warning(self, i18n.get('app.backup'), message)
        except Exception as e:
            QMessageBox.warning(self, i18n.get('app.backup'), str(e))

    def export_csv(self):
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                i18n.get('csv.export'),
                str(Path.home() / f"meditation_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"),
                "CSV Files (*.csv)"
            )
            if file_name:
                success, message = backup_manager.export_csv(
                    Path(file_name),
                    settings.date_format
                )
                if success:
                    QMessageBox.information(self, "CSV", message)
                else:
                    QMessageBox.warning(self, "CSV", message)
        except Exception as e:
            QMessageBox.warning(self, "CSV", str(e))

    def import_csv(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                i18n.get('csv.import'),
                str(Path.home()),
                "CSV Files (*.csv)"
            )
            if file_name:
                reply = QMessageBox.question(
                    self,
                    "CSV",
                    "CSVからデータをインポートします。重複するデータがある可能性があります。続行しますか？\nImporting data from CSV. There may be duplicate data. Continue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    success, message = backup_manager.import_csv(
                        Path(file_name),
                        settings.date_format
                    )
                    if success:
                        QMessageBox.information(self, "CSV", message)
                    else:
                        QMessageBox.warning(self, "CSV", message)
        except Exception as e:
            QMessageBox.warning(self, "CSV", str(e))
