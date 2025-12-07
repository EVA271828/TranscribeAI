#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试Whisper转录进度功能
"""

import os
import sys
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.whisper_transcriber import WhisperTranscriber

def test_progress_callback():
    """测试进度回调功能"""
    print("=== 测试Whisper转录进度功能 ===\n")
    
    # 创建一个简单的测试音频文件（如果不存在）
    # 这里我们假设用户有一个测试音频文件
    test_audio_file = "AI可以取代我，那我的意义是？_哔哩哔哩_bilibili.mp3"
    
    # 检查文件是否存在
    if not os.path.exists(test_audio_file):
        print(f"错误：测试音频文件 '{test_audio_file}' 不存在。")
        print("请确保有一个测试音频文件在当前目录下，或修改代码中的文件路径。")
        return False
    
    # 初始化转录器
    print("正在初始化Whisper转录器...")
    transcriber = WhisperTranscriber(model_name="tiny")  # 使用tiny模型以加快测试速度
    
    # 定义进度回调函数
    progress_values = []
    
    def progress_callback(progress):
        progress_values.append(progress)
        # 创建一个简单的进度条
        bar_length = 30
        filled_length = int(round(bar_length * progress / 100))
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        # 使用回车符覆盖当前行，实现进度条更新效果
        print(f'\r进度: |{bar}| {progress:.1f}% ', end='', flush=True)
        
        # 如果完成，打印换行
        if progress >= 100:
            print()
    
    try:
        print(f"开始转录音频文件: {test_audio_file}")
        start_time = time.time()
        
        # 使用进度回调进行转录
        transcription = transcriber.transcribe(
            test_audio_file, 
            language="zh", 
            verbose=True,  # 显示详细输出
            progress_callback=progress_callback  # 提供进度回调函数
        )
        
        end_time = time.time()
        
        # 验证结果
        print(f"\n转录完成！总耗时: {end_time - start_time:.2f}秒")
        print(f"转录文本长度: {len(transcription)}字符")
        print(f"进度回调被调用了 {len(progress_values)} 次")
        
        if progress_values:
            print(f"最小进度值: {min(progress_values)}%")
            print(f"最大进度值: {max(progress_values)}%")
            print(f"最后5个进度值: {progress_values[-5:]}")
        
        # 检查转录结果是否有效
        if len(transcription) > 0:
            print("\n转录结果预览:")
            print("-" * 50)
            print(transcription[:200] + "..." if len(transcription) > 200 else transcription)
            print("-" * 50)
            print("\n测试通过！进度回调功能正常工作。")
            return True
        else:
            print("\n警告：转录结果为空。")
            return False
            
    except Exception as e:
        print(f"\n转录过程中发生错误: {e}")
        return False

def test_without_progress_callback():
    """测试不使用进度回调的情况"""
    print("\n=== 测试不使用进度回调的情况 ===\n")
    
    test_audio_file = "AI可以取代我，那我的意义是？_哔哩哔哩_bilibili.mp3"
    
    # 检查文件是否存在
    if not os.path.exists(test_audio_file):
        print(f"错误：测试音频文件 '{test_audio_file}' 不存在。")
        return False
    
    # 初始化转录器
    print("正在初始化Whisper转录器...")
    transcriber = WhisperTranscriber(model_name="tiny")
    
    try:
        print(f"开始转录音频文件: {test_audio_file}")
        start_time = time.time()
        
        # 不使用进度回调进行转录
        transcription = transcriber.transcribe(
            test_audio_file, 
            language="zh", 
            verbose=True  # 显示详细输出
        )
        
        end_time = time.time()
        
        # 验证结果
        print(f"\n转录完成！总耗时: {end_time - start_time:.2f}秒")
        print(f"转录文本长度: {len(transcription)}字符")
        
        # 检查转录结果是否有效
        if len(transcription) > 0:
            print("\n测试通过！不使用进度回调的情况下也能正常工作。")
            return True
        else:
            print("\n警告：转录结果为空。")
            return False
            
    except Exception as e:
        print(f"\n转录过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    # 运行测试
    test1_result = test_progress_callback()
    test2_result = test_without_progress_callback()
    
    # 总结测试结果
    print("\n=== 测试总结 ===")
    print(f"带进度回调的测试: {'通过' if test1_result else '失败'}")
    print(f"不带进度回调的测试: {'通过' if test2_result else '失败'}")
    
    if test1_result and test2_result:
        print("\n所有测试通过！Whisper转录进度功能已成功实现。")
    else:
        print("\n部分测试失败，请检查实现。")