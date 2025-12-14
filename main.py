#!/usr/bin/env python3
"""
音频转录与总结工具主入口文件
"""

import sys
import os
import argparse

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.core.audio_summarizer import main as cli_main, enter_config_mode
from src.gui.main_gui import main as gui_main
from src.core.batch_process import main as batch_main

def main():
    """主程序入口"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='音频转录与总结工具')
    parser.add_argument('--cli', action='store_true',
                        help='启动命令行界面')
    parser.add_argument('--output', type=str, default=None,
                        help='指定输出文件夹路径')
    parser.add_argument('--batch', action='store_true',
                        help='批量处理模式')
    parser.add_argument('--config', action='store_true',
                        help='进入配置模式')
    args = parser.parse_args()
    
    # 根据参数选择启动模式，默认启动图形化界面
    if args.cli:
        print("启动命令行界面...")
        cli_main(args.output)
    elif args.batch:
        print("启动批量处理模式...")
        batch_main()
    elif args.config:
        print("进入配置模式...")
        from src.config.config_manager import ConfigManager
        config = ConfigManager()
        enter_config_mode(config)
    else:
        print("正在启动图形化界面...")
        gui_main()

if __name__ == "__main__":
    main()