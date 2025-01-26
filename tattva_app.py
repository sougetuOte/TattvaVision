import sys
import os
import pandas as pd
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTextEdit, QComboBox,
                            QSpinBox, QMessageBox, QFrame, QSizePolicy, QDialog)
from PySide6.QtGui import QPixmap, QFont, QPalette, QColor, QIcon
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl
from database import initialize_database, MeditationRecord, db, backup_database
from record_window import RecordWindow
from settings import settings
from i18n import i18n
from settings_window import SettingsWindow
import logging
import argparse

class StyleSheet:
    MAIN_STYLE = """
        QMainWindow {
            background-color: white;
        }
        QLabel {
            color: #333333;
        }
        QPushButton {
            background-color: #4A90E2;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #357ABD;
        }
        QPushButton:pressed {
            background-color: #2A5F94;
        }
        QPushButton:disabled {
            background-color: #CCCCCC;
        }
        QComboBox, QSpinBox {
            padding: 4px;
            border: 1px solid #CCCCCC;
            border-radius: 4px;
            background-color: white;
        }
        QTextEdit {
            border: 1px solid #CCCCCC;
            border-radius: 4px;
            background-color: white;
            padding: 8px;
        }
    """
    
    TIME_DISPLAY_STYLE = """
        QLabel {
            font-size: 48px;
            color: #4A90E2;
        }
    """
    
    TIME_INFO_STYLE = """
        QLabel {
            color: #666666;
            font-size: 12px;
        }
    """

class TattvaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        logging.debug("アプリケーションの初期化を開始")
        self.setWindowTitle(i18n.get('app.title'))
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(StyleSheet.MAIN_STYLE)
        
        # Initialize database and other components
        initialize_database()
        
        # Set application icon
        app_icon = QIcon('images/tattvavision.ico')
        self.setWindowIcon(app_icon)
        QApplication.instance().setWindowIcon(app_icon)
        logging.debug("アプリケーションアイコンを設定")
        
        # Initialize UI components
        self.setup_timers()
        self.setup_sound_player()
        self.load_tattva_data()
        logging.debug("UIコンポーネントの初期化完了")
        
        # Create main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Left panel
        left_panel = self.create_left_panel()
        layout.addWidget(left_panel)
        
        # Center panel
        center_panel = self.create_center_panel()
        layout.addWidget(center_panel)
        
        # Right panel
        right_panel = self.create_right_panel()
        layout.addWidget(right_panel)
        
        # Set stretch factors
        layout.setStretch(0, 1)  # Left panel
        layout.setStretch(1, 2)  # Center panel
        layout.setStretch(2, 1)  # Right panel
        
        self.setMinimumSize(1000, 600)
        self.update_card_display()

    def setup_timers(self):
        self.meditation_timer = QTimer()
        self.meditation_timer.timeout.connect(self.update_meditation_time)
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.remaining_seconds = 0
        self.countdown_seconds = 5
        self.meditation_start_time = None
        self.meditation_end_time = None

    def create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(16)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Card selection
        layout.addWidget(QLabel(i18n.get('card_selection.title')))
        self.card_combo = QComboBox()
        self.card_combo.addItems([row['組み合わせ'] 
                                for _, row in self.tattva_data.iterrows() if pd.notna(row['組み合わせ'])])
        self.card_combo.currentIndexChanged.connect(self.update_card_display)
        layout.addWidget(self.card_combo)
        
        # Timer selection
        layout.addWidget(QLabel(i18n.get('timer.title')))
        self.timer_spinbox = QSpinBox()
        self.timer_spinbox.setRange(1, 60)
        self.timer_spinbox.setValue(10)
        self.timer_spinbox.setSuffix(i18n.get('timer.minutes'))
        layout.addWidget(self.timer_spinbox)
        
        # Time display
        time_widget = QWidget()
        time_layout = QVBoxLayout(time_widget)
        time_layout.setSpacing(4)
        
        self.time_display = QLabel("00:00")
        self.time_display.setStyleSheet(StyleSheet.TIME_DISPLAY_STYLE)
        self.time_display.setAlignment(Qt.AlignCenter)
        time_layout.addWidget(self.time_display)
        
        self.start_time_label = QLabel(f"{i18n.get('timer.start_time')}: --:--:--")
        self.end_time_label = QLabel(f"{i18n.get('timer.end_time')}: --:--:--")
        self.duration_label = QLabel(f"{i18n.get('timer.duration')}: --{i18n.get('timer.minutes')}")
        
        for label in [self.start_time_label, self.end_time_label, self.duration_label]:
            label.setStyleSheet(StyleSheet.TIME_INFO_STYLE)
            time_layout.addWidget(label)
        
        layout.addWidget(time_widget)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton(i18n.get('control.start'))
        self.start_button.clicked.connect(self.start_meditation)
        self.stop_button = QPushButton(i18n.get('control.stop'))
        self.stop_button.clicked.connect(self.stop_meditation)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("background-color: #CCCCCC;")
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)
        
        layout.addStretch()
        return panel

    def create_center_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(16)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        layout.addWidget(QLabel(i18n.get('card.title')))
        
        # Card image
        self.card_image = QLabel()
        self.card_image.setFixedSize(300, 300)
        self.card_image.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.card_image, alignment=Qt.AlignCenter)
        
        # Interpretation
        layout.addWidget(QLabel(i18n.get('interpretation.title')))
        self.pos_interpret = QLabel(f"{i18n.get('interpretation.positive')}:")
        self.pos_interpret.setWordWrap(True)
        self.neg_interpret = QLabel(f"{i18n.get('interpretation.negative')}:")
        self.neg_interpret.setWordWrap(True)
        
        layout.addWidget(self.pos_interpret)
        layout.addWidget(self.neg_interpret)
        
        layout.addStretch()
        return panel

    def create_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(16)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Notes
        layout.addWidget(QLabel(i18n.get('notes.title')))
        self.notes = QTextEdit()
        self.notes.setPlaceholderText(i18n.get('notes.placeholder'))
        layout.addWidget(self.notes)
        
        # Record management
        layout.addWidget(QLabel(i18n.get('record.title')))
        
        button_layout = QHBoxLayout()
        
        save_button = QPushButton(i18n.get('record.save'))
        save_button.clicked.connect(self.save_meditation)
        button_layout.addWidget(save_button)
        
        record_button = QPushButton(i18n.get('record.list'))
        record_button.clicked.connect(self.show_record_list)
        button_layout.addWidget(record_button)
        
        settings_button = QPushButton("⚙️ " + i18n.get('app.settings'))
        settings_button.clicked.connect(self.show_settings)
        button_layout.addWidget(settings_button)
        
        layout.addLayout(button_layout)
        
        return panel

    def load_tattva_data(self):
        """タットワデータの読み込み"""
        try:
            self.tattva_data = pd.read_csv('tattva.csv', encoding='utf-8')
            logging.debug(f"タットワデータを読み込みました: {len(self.tattva_data)}行")
        except Exception as e:
            logging.error(f"タットワデータの読み込みに失敗: {str(e)}")
            self.tattva_data = pd.DataFrame()

    def setup_sound_player(self):
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        
        # Set the source to the MP3 file
        self.player.setSource(QUrl.fromLocalFile(os.path.abspath("copper-bell-ding-25-204990.mp3")))
        self.audio_output.setVolume(1.0)

    def play_sound(self):
        self.player.setPosition(0)  # Reset to start
        self.player.play()

    def update_card_display(self):
        """カード表示を更新"""
        try:
            selected_card = self.card_combo.currentText()
            logging.debug(f"選択されたカード: {selected_card}")
            
            if selected_card and selected_card in self.tattva_data['組み合わせ'].values:
                card_data = self.tattva_data[self.tattva_data['組み合わせ'] == selected_card].iloc[0]
                
                # カード画像の表示
                image_path = os.path.join('images', card_data['画像ファイル名'])
                if os.path.exists(image_path):
                    pixmap = QPixmap(image_path)
                    if not pixmap.isNull():
                        # サイズチェック（201x257であることを確認）
                        if pixmap.width() == 201 and pixmap.height() == 257:
                            # 表示サイズに合わせてスケーリング（アスペクト比を保持）
                            self.card_image.setPixmap(pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio))
                            logging.debug(f"カード画像を読み込みました: {image_path}")
                else:
                    logging.warning(f"カード画像が見つかりません: {image_path}")
                    self.card_image.clear()
                
                # 解釈の表示
                pos_text = card_data['ポジティブ解釈'] if pd.notna(card_data['ポジティブ解釈']) else "解釈なし"
                neg_text = card_data['ネガティブ解釈'] if pd.notna(card_data['ネガティブ解釈']) else "解釈なし"
                
                self.pos_interpret.setText(f"{i18n.get('interpretation.positive')}: {pos_text}")
                self.neg_interpret.setText(f"{i18n.get('interpretation.negative')}: {neg_text}")
            else:
                logging.warning(f"選択されたカード {selected_card} のデータが見つかりません")
                self.card_image.clear()
                self.pos_interpret.clear()
                self.neg_interpret.clear()
        except Exception as e:
            logging.error(f"カード表示の更新中にエラーが発生: {str(e)}")

    def start_meditation(self):
        """瞑想を開始"""
        try:
            self.start_time_label.setText(f"{i18n.get('timer.start_time')}: --:--:--")
            self.end_time_label.setText(f"{i18n.get('timer.end_time')}: --:--:--")
            self.duration_label.setText(f"{i18n.get('timer.duration')}: --{i18n.get('timer.minutes')}")
            
            self.remaining_seconds = self.timer_spinbox.value() * 60
            self.countdown_seconds = 5
            
            # Disable start button and enable stop button
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.timer_spinbox.setEnabled(False)
            
            # Start countdown
            self.update_countdown()
            self.countdown_timer.start(1000)  # 1秒ごとに更新
            logging.debug("瞑想開始")
        except Exception as e:
            logging.error(f"瞑想開始時にエラーが発生: {str(e)}")

    def update_countdown(self):
        if self.countdown_seconds > 0:
            self.time_display.setText(f"{i18n.get('timer.countdown')}: {self.countdown_seconds}")
            self.countdown_seconds -= 1
        else:
            self.countdown_timer.stop()
            self.play_sound()  # 開始音
            self.meditation_start_time = datetime.now()
            self.start_time_label.setText(f"{i18n.get('timer.start_time')}: {self.meditation_start_time.strftime('%H:%M:%S')}")
            self.meditation_timer.start(1000)
            self.update_meditation_time()

    def update_meditation_time(self):
        if self.remaining_seconds > 0:
            minutes = self.remaining_seconds // 60
            seconds = self.remaining_seconds % 60
            self.time_display.setText(f"{minutes:02d}:{seconds:02d}")
            self.remaining_seconds -= 1
        else:
            self.meditation_timer.stop()
            self.play_sound()  # 終了音
            self.meditation_end_time = datetime.now()
            self.stop_meditation()

    def stop_meditation(self):
        self.meditation_timer.stop()
        self.countdown_timer.stop()
        
        if not self.meditation_end_time:
            self.meditation_end_time = datetime.now()
        
        # Update time labels
        self.end_time_label.setText(f"{i18n.get('timer.end_time')}: {self.meditation_end_time.strftime('%H:%M:%S')}")
        duration = (self.meditation_end_time - self.meditation_start_time).total_seconds() / 60
        self.duration_label.setText(f"{i18n.get('timer.duration')}: {duration:.1f}{i18n.get('timer.minutes')}")
        
        # Reset UI
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.timer_spinbox.setEnabled(True)
        self.time_display.setText("00:00")

    def save_meditation(self):
        if not self.meditation_start_time or not self.meditation_end_time:
            QMessageBox.warning(
                self,
                i18n.get('error.title'),
                i18n.get('error.no_meditation')
            )
            return
        
        try:
            duration = (self.meditation_end_time - self.meditation_start_time).total_seconds() / 60
            
            with db.atomic():
                record = MeditationRecord.create(
                    date=self.meditation_start_time,
                    start_time=self.meditation_start_time,
                    end_time=self.meditation_end_time,
                    duration=int(duration),
                    card_name=self.card_combo.currentText(),
                    notes=self.notes.toPlainText()
                )
            
            # Reset after successful save
            self.notes.clear()
            self.meditation_start_time = None
            self.meditation_end_time = None
            self.start_time_label.setText(f"{i18n.get('timer.start_time')}: --:--:--")
            self.end_time_label.setText(f"{i18n.get('timer.end_time')}: --:--:--")
            self.duration_label.setText(f"{i18n.get('timer.duration')}: --{i18n.get('timer.minutes')}")
            
            QMessageBox.information(
                self,
                i18n.get('success.title'),
                i18n.get('success.record_saved')
            )
            
        except Exception as e:
            QMessageBox.warning(
                self,
                i18n.get('error.title'),
                f"{i18n.get('error.save_failed')}: {str(e)}"
            )

    def show_record_list(self):
        self.record_window = RecordWindow()
        self.record_window.show()

    def show_settings(self):
        dialog = SettingsWindow(self)
        if dialog.exec_() == QDialog.Accepted:
            self.reload_ui_texts()

    def reload_ui_texts(self):
        """UIのテキストを現在の言語設定で更新"""
        self.setWindowTitle(i18n.get('app.title'))
        self.timer_spinbox.setSuffix(i18n.get('timer.minutes'))
        self.start_time_label.setText(f"{i18n.get('timer.start_time')}: --:--:--")
        self.end_time_label.setText(f"{i18n.get('timer.end_time')}: --:--:--")
        self.duration_label.setText(f"{i18n.get('timer.duration')}: --{i18n.get('timer.minutes')}")
        self.start_button.setText(i18n.get('control.start'))
        self.stop_button.setText(i18n.get('control.stop'))
        self.notes.setPlaceholderText(i18n.get('notes.placeholder'))
        self.update_card_display()

    def closeEvent(self, event):
        """アプリケーション終了時の処理"""
        # データベースのバックアップを作成
        backup_database()
        db.close()
        event.accept()

def setup_logging(debug_mode=False):
    """ロギングの設定"""
    log_level = logging.DEBUG if debug_mode else logging.ERROR
    log_format = '%(asctime)s - %(levelname)s - %(message)s' if debug_mode else '%(message)s'
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler()]
    )

def parse_arguments():
    """コマンドライン引数の解析"""
    parser = argparse.ArgumentParser(description='TattvaVision - タットワ瞑想支援アプリケーション')
    parser.add_argument('--debug', action='store_true', help='デバッグモードで起動（詳細なログを表示）')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    setup_logging(args.debug)
    
    try:
        app = QApplication(sys.argv)
        window = TattvaApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"アプリケーションの起動に失敗しました: {str(e)}")
        sys.exit(1)