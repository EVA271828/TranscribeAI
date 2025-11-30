#!/usr/bin/env python3
"""
启动图形化界面的快捷脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.gui.main_gui import main

if __name__ == "__main__":
    main()