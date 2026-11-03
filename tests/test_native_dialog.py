import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))
import native_dialog


def test_parse_picker_payload_reads_json_and_bare_paths():
    parsed = native_dialog.parse_picker_payload(
        '{"path":"D:\\\\测试\\\\case","error":"","engine":"shbrowse","cancelled":false}')
    assert parsed['path'] == 'D:\\测试\\case'
    assert parsed['done'] is True
    assert parsed['cancelled'] is False
    bare = native_dialog.parse_picker_payload(r'D:\cases\NativeTest')
    assert bare['path'] == r'D:\cases\NativeTest'
    assert bare['cancelled'] is False
    empty = native_dialog.parse_picker_payload('')
    assert empty['path'] == ''
    assert empty['cancelled'] is True


def test_choose_directory_without_windows_does_not_crash():
    result = native_dialog.choose_directory(r'D:\cases')
    assert result.path == ''
    assert result.cancelled is True
    assert result.error
