import os
from pydub import AudioSegment
from pydub.playback import play

class SoundManager:
    def __init__(self):
        self.volume_level = 100  # デフォルトは最大音量
        self.start_sound_path = os.path.join("sounds", "start.mp3")
        self.end_sound_path = os.path.join("sounds", "end.mp3")
        self._volume_db = 0  # 0 dB = 最大音量

    def play_start_sound(self):
        """開始音を再生する"""
        try:
            sound = AudioSegment.from_mp3(self.start_sound_path)
            sound = sound + self._volume_db  # 音量を調整
            play(sound)
        except FileNotFoundError:
            raise FileNotFoundError(f"開始音ファイルが見つかりません: {self.start_sound_path}")
        except Exception as e:
            raise Exception(f"音声再生エラー: {str(e)}")

    def play_end_sound(self):
        """終了音を再生する"""
        try:
            sound = AudioSegment.from_mp3(self.end_sound_path)
            sound = sound + self._volume_db  # 音量を調整
            play(sound)
        except FileNotFoundError:
            raise FileNotFoundError(f"終了音ファイルが見つかりません: {self.end_sound_path}")
        except Exception as e:
            raise Exception(f"音声再生エラー: {str(e)}")

    def set_volume(self, level):
        """音量レベルを設定する（0-100）"""
        self.volume_level = max(0, min(100, level))
        if self.volume_level == 0:
            self._volume_db = float('-inf')  # ミュート
        else:
            # 音量レベルをデシベルに変換（0-100を0から-30 dBの範囲にマッピング）
            self._volume_db = -30 * (1 - self.volume_level / 100)

    def get_volume_db(self):
        """現在の音量レベルをデシベルで返す"""
        return self._volume_db
