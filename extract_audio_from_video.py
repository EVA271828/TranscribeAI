#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频音频提取工具
使用FFmpeg从视频文件中提取音频，并保持源文件夹结构
"""

import os
import subprocess
import sys
from pathlib import Path
import argparse


def check_ffmpeg_exists(ffmpeg_path):
    """检查FFmpeg是否存在"""
    if not os.path.exists(ffmpeg_path):
        print(f"错误: FFmpeg未找到于路径 {ffmpeg_path}")
        return False
    return True


def get_video_files(directory):
    """获取目录中的所有视频文件"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp']
    video_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(os.path.join(root, file))
    
    return video_files


def extract_audio(ffmpeg_path, input_file, output_file):
    """使用FFmpeg提取音频"""
    # 检查输出文件是否已存在
    if os.path.exists(output_file):
        print(f"跳过已存在的文件: {output_file}")
        return True
    
    try:
        # 使用FFmpeg提取音频并转换为WAV格式（Whisper支持的格式）
        cmd = [
            ffmpeg_path,
            '-i', input_file,
            '-vn',  # 不包含视频流
            '-acodec', 'pcm_s16le',  # 音频编码为PCM 16位
            '-ar', '16000',  # 采样率16kHz（Whisper推荐）
            '-ac', '1',  # 单声道
            '-y',  # 覆盖输出文件
            output_file
        ]
        
        print(f"正在处理: {input_file}")
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"音频已提取: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"处理 {input_file} 时出错: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='从视频文件中提取音频')
    parser.add_argument('source_dir', help='源文件夹路径')
    parser.add_argument('target_dir', help='目标文件夹路径')
    parser.add_argument('--ffmpeg-path', default='D:\\software\\ffmpeg-master-latest-win64-gpl-shared\\bin\\ffmpeg.exe',
                       help='FFmpeg可执行文件路径')
    
    args = parser.parse_args()
    
    source_dir = os.path.abspath(args.source_dir)
    target_dir = os.path.abspath(args.target_dir)
    ffmpeg_path = args.ffmpeg_path
    
    # 检查FFmpeg是否存在
    if not check_ffmpeg_exists(ffmpeg_path):
        sys.exit(1)
    
    # 检查源目录是否存在
    if not os.path.exists(source_dir):
        print(f"错误: 源目录不存在: {source_dir}")
        sys.exit(1)
    
    # 创建目标目录（如果不存在）
    os.makedirs(target_dir, exist_ok=True)
    
    # 获取所有视频文件
    video_files = get_video_files(source_dir)
    
    if not video_files:
        print("未找到任何视频文件")
        return
    
    print(f"找到 {len(video_files)} 个视频文件")
    
    success_count = 0
    failure_count = 0
    
    # 处理每个视频文件
    for video_file in video_files:
        # 计算相对路径，以保持源文件夹结构
        rel_path = os.path.relpath(video_file, source_dir)
        
        # 更改扩展名为.wav
        rel_dir = os.path.dirname(rel_path)
        filename = os.path.basename(rel_path)
        name_without_ext = os.path.splitext(filename)[0]
        output_filename = f"{name_without_ext}.wav"
        
        # 创建目标目录结构
        if rel_dir:
            output_dir = os.path.join(target_dir, rel_dir)
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = target_dir
        
        output_file = os.path.join(output_dir, output_filename)
        
        # 提取音频
        if extract_audio(ffmpeg_path, video_file, output_file):
            success_count += 1
        else:
            failure_count += 1
    
    print(f"\n处理完成!")
    print(f"成功: {success_count} 个文件")
    print(f"失败: {failure_count} 个文件")


if __name__ == "__main__":
    main()