#!/usr/bin/env python3
"""
音频转录与总结工具主入口文件
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.audio_summarizer import main

if __name__ == "__main__":
    main()