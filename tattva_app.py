import sys
import os
import pandas as pd
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTextEdit, QComboBox,
                            QSpinBox, QMessageBox, QFrame, QSizePolicy)
from PySide6.QtGui import QPixmap, QFont, QPalette, QColor, QIcon
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl
from database import initialize_database, MeditationRecord, db
from record_window import RecordWindow

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
        self.setWindowTitle("タットワ瞑想記録")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(StyleSheet.MAIN_STYLE)
        
        # Initialize database and other components
        initialize_database()
        self.setup_timers()
        self.setup_sound_player()
        self.load_tattva_data()
        
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
        layout.addWidget(QLabel("カード選択"))
        self.card_combo = QComboBox()
        self.card_combo.addItems([row['組み合わせ'] 
                                for _, row in self.tattva_data.iterrows() if pd.notna(row['組み合わせ'])])
        self.card_combo.currentIndexChanged.connect(self.update_card_display)
        layout.addWidget(self.card_combo)
        
        # Timer selection
        layout.addWidget(QLabel("瞑想時間"))
        self.timer_spinbox = QSpinBox()
        self.timer_spinbox.setRange(1, 60)
        self.timer_spinbox.setValue(10)
        self.timer_spinbox.setSuffix("分")
        layout.addWidget(self.timer_spinbox)
        
        # Time display
        time_widget = QWidget()
        time_layout = QVBoxLayout(time_widget)
        time_layout.setSpacing(4)
        
        self.time_display = QLabel("00:00")
        self.time_display.setStyleSheet(StyleSheet.TIME_DISPLAY_STYLE)
        self.time_display.setAlignment(Qt.AlignCenter)
        time_layout.addWidget(self.time_display)
        
        self.start_time_label = QLabel("開始時刻: --:--:--")
        self.end_time_label = QLabel("終了時刻: --:--:--")
        self.duration_label = QLabel("瞑想時間: --分")
        
        for label in [self.start_time_label, self.end_time_label, self.duration_label]:
            label.setStyleSheet(StyleSheet.TIME_INFO_STYLE)
            time_layout.addWidget(label)
        
        layout.addWidget(time_widget)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("開始")
        self.start_button.clicked.connect(self.start_meditation)
        self.stop_button = QPushButton("停止")
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
        layout.addWidget(QLabel("タットワカード"))
        
        # Card image
        self.card_image = QLabel()
        self.card_image.setFixedSize(300, 300)
        self.card_image.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.card_image, alignment=Qt.AlignCenter)
        
        # Interpretation
        layout.addWidget(QLabel("解釈"))
        self.pos_interpret = QLabel("ポジティブな解釈:")
        self.pos_interpret.setWordWrap(True)
        self.neg_interpret = QLabel("ネガティブな解釈:")
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
        layout.addWidget(QLabel("瞑想記録"))
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("瞑想中の気づきや感想をメモしましょう...")
        layout.addWidget(self.notes)
        
        # Record management
        layout.addWidget(QLabel("記録管理"))
        save_button = QPushButton("記録を保存")
        save_button.clicked.connect(self.save_meditation)
        layout.addWidget(save_button)
        
        record_button = QPushButton("記録一覧")
        record_button.clicked.connect(self.show_record_list)
        layout.addWidget(record_button)
        
        return panel

    def load_tattva_data(self):
        self.tattva_data = pd.read_csv('tattva.csv', encoding='utf-8')

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
        current_text = self.card_combo.currentText()
        if current_text:
            matching_rows = self.tattva_data[self.tattva_data['組み合わせ'] == current_text]
            
            if not matching_rows.empty:
                row = matching_rows.iloc[0]
                
                # Update image
                image_path = os.path.join('images', row['画像ファイル名'])
                if os.path.exists(image_path):
                    pixmap = QPixmap(image_path)
                    self.card_image.setPixmap(pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio))
                
                # Update interpretations
                pos_text = row['ポジティブ解釈'] if pd.notna(row['ポジティブ解釈']) else "解釈なし"
                neg_text = row['ネガティブ解釈'] if pd.notna(row['ネガティブ解釈']) else "解釈なし"
                
                self.pos_interpret.setText(f"ポジティブな解釈:\n{pos_text}")
                self.neg_interpret.setText(f"ネガティブな解釈:\n{neg_text}")

    def start_meditation(self):
        # meditation_start_timeはカウントダウン終了後に設定するため、ここでは設定しない
        self.start_time_label.setText("開始時刻: --:--:--")
        self.end_time_label.setText("終了時刻: --:--:--")
        self.duration_label.setText("瞑想時間: --分")
        
        self.remaining_seconds = self.timer_spinbox.value() * 60
        self.countdown_seconds = 5
        
        # Disable start button and enable stop button
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.timer_spinbox.setEnabled(False)
        
        # Start countdown
        self.update_countdown()
        self.countdown_timer.start(1000)  # 1秒ごとに更新

    def update_countdown(self):
        if self.countdown_seconds > 0:
            self.time_display.setText(f"開始まで: {self.countdown_seconds}")
            self.countdown_seconds -= 1
        else:
            self.countdown_timer.stop()
            self.play_sound()  # 開始音
            # 実際の瞑想開始時に開始時刻を設定
            self.meditation_start_time = datetime.now()
            self.start_time_label.setText(f"開始時刻: {self.meditation_start_time.strftime('%H:%M:%S')}")
            self.meditation_timer.start(1000)  # 1秒ごとに更新
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
        self.end_time_label.setText(f"終了時刻: {self.meditation_end_time.strftime('%H:%M:%S')}")
        duration = (self.meditation_end_time - self.meditation_start_time).total_seconds() / 60
        self.duration_label.setText(f"瞑想時間: {duration:.1f}分")
        
        # Reset UI
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.timer_spinbox.setEnabled(True)
        self.time_display.setText("00:00")

    def save_meditation(self):
        if not self.meditation_start_time or not self.meditation_end_time:
            QMessageBox.warning(self, "エラー", "瞑想を実施してから保存してください。")
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
            self.start_time_label.setText("開始時刻: --:--:--")
            self.end_time_label.setText("終了時刻: --:--:--")
            self.duration_label.setText("瞑想時間: --分")
            
            QMessageBox.information(self, "成功", "記録を保存しました。")
            
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"保存に失敗しました: {str(e)}")

    def show_record_list(self):
        self.record_window = RecordWindow()
        self.record_window.show()

    def closeEvent(self, event):
        db.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TattvaApp()
    window.show()
    sys.exit(app.exec())