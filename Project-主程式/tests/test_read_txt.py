"""read_txt.Recent_info() 的失效行為測試（不需 TensorFlow / OpenCV / MediaPipe）。

涵蓋審查指出的三個崩潰情境：檔案不存在、空檔、最後一行沒有結尾換行。
"""
import os

import read_txt


def writeRoutePlan(tmp_path, content, newline = True):
    outputDir = tmp_path / 'output'
    outputDir.mkdir(exist_ok=True)
    path = outputDir / 'routePlan.txt'
    path.write_text(content + ('\n' if newline else ''), encoding='utf-8')
    return path


def test_normal_line(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    writeRoutePlan(tmp_path, '250~中山北路~90~180~TURN_LEFT')
    assert read_txt.Recent_info() == (250, '中山北路', 90, 180, 'TURN_LEFT')


def test_last_line_without_newline_keeps_END(tmp_path, monkeypatch):
    # 舊寫法用 [:-1] 砍掉最後一個字，會把 END 變成 EN 而誤判尚未抵達終點
    monkeypatch.chdir(tmp_path)
    writeRoutePlan(tmp_path, '12~MainSt~0~90~END', newline=False)
    assert read_txt.Recent_info() == (12, 'MainSt', 0, 90, 'END')


def test_only_last_record_is_used(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    lines = ['%d~Road%d~0~90~STRAIGHT'%(i, i) for i in range(2000)]
    lines.append('7~忠孝東路~45~270~TURN_RIGHT')
    writeRoutePlan(tmp_path, '\n'.join(lines))
    assert read_txt.Recent_info() == (7, '忠孝東路', 45, 270, 'TURN_RIGHT')


def test_long_last_line_across_blocks(tmp_path, monkeypatch):
    # 最後一行比讀取區塊大時要能往前擴張，不能只讀到半行
    monkeypatch.chdir(tmp_path)
    name = 'A' * 5000
    writeRoutePlan(tmp_path, '1~Old~0~0~END\n30~%s~45~270~TURN_RIGHT'%name)
    assert read_txt.Recent_info() == (30, name, 45, 270, 'TURN_RIGHT')


def test_empty_file_returns_none(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    writeRoutePlan(tmp_path, '', newline=False)
    assert read_txt.Recent_info() is None


def test_missing_file_returns_none(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert not os.path.exists('output/routePlan.txt')
    assert read_txt.Recent_info() is None


def test_comma_separated_line_returns_none(tmp_path, monkeypatch):
    # 舊版 Android 端送的逗號格式：不該再拋 ValueError 炸掉主迴圈
    monkeypatch.chdir(tmp_path)
    writeRoutePlan(tmp_path, '250,中山路,90,180,TURN_LEFT')
    assert read_txt.Recent_info() is None


def test_too_few_fields_returns_none(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    writeRoutePlan(tmp_path, '250~中山路~90')
    assert read_txt.Recent_info() is None


def test_non_numeric_field_returns_none(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    writeRoutePlan(tmp_path, 'NaN~中山路~90~180~END')
    assert read_txt.Recent_info() is None


def test_recent_hand_info(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert read_txt.Recent_hand_info() is None            # 檔案不存在
    (tmp_path / 'handRecognition.txt').write_text('Open\nClose', encoding='utf-8')
    assert read_txt.Recent_hand_info() == 'Close'         # 無結尾換行也要完整取回
