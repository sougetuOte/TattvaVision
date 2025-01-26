import pytest
from unittest.mock import Mock, patch
import os
import tempfile
from pathlib import Path
from sound_manager import SoundManager

@pytest.fixture
def sound_manager():
    """テスト用のSoundManagerインスタンスを提供する"""
    manager = SoundManager()
    # テスト用のパスを設定（実際のファイルは不要）
    sound_path = str(Path(__file__).parent.parent / "fixtures" / "sounds" / "test_bell.mp3")
    manager.start_sound_path = sound_path
    manager.end_sound_path = sound_path
    return manager

@patch('pydub.AudioSegment')
@patch('pydub.playback')
def test_play_start_sound(mock_playback, mock_audio_segment, sound_manager):
    """開始音の再生テスト（完全モック化）"""
    # モックの設定
    mock_sound = Mock()
    mock_audio_segment.from_mp3.return_value = mock_sound
    mock_sound.__add__ = lambda x: mock_sound  # 音量調整のための加算をモック
    
    # 開始音の再生
    sound_manager.play_start_sound()
    
    # モックが正しく呼び出されたか確認
    mock_audio_segment.from_mp3.assert_called_once_with(sound_manager.start_sound_path)
    mock_playback.play.assert_called_once_with(mock_sound)

@patch('pydub.AudioSegment')
@patch('pydub.playback')
def test_play_end_sound(mock_playback, mock_audio_segment, sound_manager):
    """終了音の再生テスト（完全モック化）"""
    # モックの設定
    mock_sound = Mock()
    mock_audio_segment.from_mp3.return_value = mock_sound
    mock_sound.__add__ = lambda x: mock_sound  # 音量調整のための加算をモック
    
    # 終了音の再生
    sound_manager.play_end_sound()
    
    # モックが正しく呼び出されたか確認
    mock_audio_segment.from_mp3.assert_called_once_with(sound_manager.end_sound_path)
    mock_playback.play.assert_called_once_with(mock_sound)

@pytest.mark.parametrize("volume_level,expected_db", [
    (0, float('-inf')),  # ミュート
    (50, -15),           # 中間
    (100, 0),           # 最大
])
def test_volume_adjustment(sound_manager, volume_level, expected_db):
    """音量調整テスト"""
    # 音量の設定
    sound_manager.set_volume(volume_level)
    
    # 音量レベルの確認
    if volume_level == 0:
        assert sound_manager.get_volume_db() == float('-inf')
    else:
        assert abs(sound_manager.get_volume_db() - expected_db) < 0.1

@patch('pydub.AudioSegment')
def test_sound_file_not_found(mock_audio_segment, sound_manager):
    """存在しない音声ファイルのエラーハンドリングテスト"""
    # AudioSegmentがFileNotFoundErrorを発生させるように設定
    mock_audio_segment.from_mp3.side_effect = FileNotFoundError()
    
    with pytest.raises(FileNotFoundError):
        sound_manager.play_start_sound()

@patch('pydub.AudioSegment')
def test_invalid_sound_file(mock_audio_segment, sound_manager):
    """無効な音声ファイルのエラーハンドリングテスト"""
    # AudioSegmentが例外を発生させるように設定
    mock_audio_segment.from_mp3.side_effect = Exception("Invalid audio file")
    
    with pytest.raises(Exception):
        sound_manager.play_start_sound()
