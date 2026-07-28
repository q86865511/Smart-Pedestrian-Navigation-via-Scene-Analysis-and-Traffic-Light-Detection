"""讓 tests/ 內的測試能匯入 Project-主程式 下的模組。

marking.py 在匯入時就會讀 arrow.png（相對路徑），所以先切到專案目錄再讓測試匯入。
"""
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, PROJECT_DIR)
os.chdir(PROJECT_DIR)
