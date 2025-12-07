#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Whisper转录进度示例
演示如何使用WhisperTranscriber的进度回调功能
"""

import os
import sys
import time
import threading

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.whisper_transcriber import WhisperTranscriber

def progress_callback(progress):
    """进度回调函数"""
    # 创建一个简单的进度条
    bar_length = 50
    filled_length = int(round(bar_length * progress / 100))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    
    # 使用回车符覆盖当前行，实现进度条更新效果
    print(f'\r进度: |{bar}| {progress:.1f}% ', end='', flush=True)
    
    # 如果完成，打印换行
    if progress >= 100:
        print()

def main():
    """主函数"""
    print("=== Whisper转录进度示例 ===\n")
    
    # 音频文件路径
    audio_file = "AI可以取代我，那我的意义是？_哔哩哔哩_bilibili.mp3"
    
    # 检查文件是否存在
    if not os.path.exists(audio_file):
        print(f"错误：音频文件 '{audio_file}' 不存在。")
        print("请确保音频文件在当前目录下，或修改代码中的文件路径。")
        return
    
    # 初始化转录器
    print("正在初始化Whisper转录器...")
    transcriber = WhisperTranscriber(model_name="base")  # 使用base模型以获得更好的平衡
    
    try:
        print(f"开始转录音频文件: {audio_file}")
        print("进度显示:")
        
        # 使用进度回调进行转录
        start_time = time.time()
        transcription = transcriber.transcribe(
            audio_file, 
            language="zh", 
            verbose=True,  # 显示详细输出
            progress_callback=progress_callback  # 提供进度回调函数
        )
        end_time = time.time()
        
        print(f"\n转录完成！总耗时: {end_time - start_time:.2f}秒")
        print(f"转录文本长度: {len(transcription)}字符")
        print("\n转录结果预览:")
        print("-" * 50)
        print(transcription[:200] + "..." if len(transcription) > 200 else transcription)
        print("-" * 50)
        
    except Exception as e:
        print(f"\n转录过程中发生错误: {e}")

if __name__ == "__main__":
    main()