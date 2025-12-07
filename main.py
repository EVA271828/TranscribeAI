#!/usr/bin/env python3
"""
音频转录与总结工具主入口文件
"""

import sys
import os
import argparse

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.audio_summarizer import main as cli_main
from src.gui.main_gui import main as gui_main

def main():
    """主程序入口"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='音频转录与总结工具')
    parser.add_argument('--gui', action='store_true',
                        help='启动图形化界面')
    parser.add_argument('--output', type=str, default=None,
                        help='指定输出文件夹路径')
    args = parser.parse_args()
    
    # 根据参数选择启动模式
    if args.gui:
        print("正在启动图形化界面...")
        gui_main()
    else:
        print("启动命令行界面...")
        cli_main(args.output)

if __name__ == "__main__":
    main()