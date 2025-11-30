#!/usr/bin/env python3
"""
测试GUI代码是否有语法错误
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.gui.main_gui import AudioTranscriberGUI
    print("GUI代码语法检查通过")
    print("AudioTranscriberGUI类已成功导入")
except ImportError as e:
    print(f"导入错误: {e}")
except SyntaxError as e:
    print(f"语法错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")