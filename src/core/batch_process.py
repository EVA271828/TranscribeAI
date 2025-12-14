#!/usr/bin/env python3
"""
批处理脚本：处理整个文件夹中的音频文件，并保持源文件夹结构
"""

import os
import sys
import argparse
import threading
import queue
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.whisper_transcriber import WhisperTranscriber
from src.core.deepseek_summarizer import DeepSeekSummarizer
from src.utils.file_utils import FileUtils
from src.config.config_manager import ConfigManager

def scan_audio_files(source_folder):
    """扫描文件夹中的所有音频文件，保持源文件夹结构"""
    audio_files = []
    
    # 支持的音频文件扩展名
    audio_extensions = ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma']
    
    # 递归扫描文件夹
    for root, _, files in os.walk(source_folder):
        for file in files:
            # 检查文件扩展名
            if any(file.lower().endswith(ext) for ext in audio_extensions):
                full_path = os.path.join(root, file)
                
                # 计算相对于源文件夹的路径
                rel_path = os.path.relpath(full_path, source_folder)
                
                audio_files.append((full_path, rel_path))
    
    return audio_files

def process_audio_file(audio_file_tuple, transcriber, summarizer, output_folder, template, source_folder, progress_queue):
    """处理单个音频文件"""
    full_path, rel_path = audio_file_tuple
    
    try:
        # 更新状态：开始处理
        progress_queue.put({'file': full_path, 'rel_path': rel_path, 'status': '开始转录', 'progress': 0})
        
        # 转录音频
        transcription = transcriber.transcribe(full_path)
        
        # 更新状态：转录完成，开始总结
        progress_queue.put({'file': full_path, 'rel_path': rel_path, 'status': '转录完成，开始总结', 'progress': 50})
        
        # 生成总结
        audio_title = FileUtils.get_audio_title(full_path)
        summary = summarizer.summarize(transcription, audio_title, template)
        
        # 保存结果，保持源文件夹结构
        transcript_file, summary_file = FileUtils.save_results(
            transcription, summary, full_path, output_folder, rel_path
        )
        
        # 更新状态：完成
        progress_queue.put({'file': full_path, 'rel_path': rel_path, 'status': '完成', 'progress': 100, 
                           'transcript_file': transcript_file, 'summary_file': summary_file})
        
    except Exception as e:
        # 更新状态：错误
        progress_queue.put({'file': full_path, 'rel_path': rel_path, 'status': f'错误: {str(e)}', 'progress': 0})
        print(f"处理文件 {rel_path} 时出错: {str(e)}")

def main():
    """主程序"""
    # 初始化配置管理器
    config = ConfigManager()
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='批量处理音频文件，保持源文件夹结构')
    parser.add_argument('--source_folder', type=str, required=True,
                        help='源文件夹路径（包含音频文件）')
    parser.add_argument('--output', type=str, required=True,
                        help='输出文件夹路径')
    parser.add_argument('--model', type=str, 
                        choices=['tiny', 'base', 'small', 'medium', 'large'],
                        help='选择Whisper模型大小')
    parser.add_argument('--api_key', type=str,
                        help='DeepSeek API密钥')
    parser.add_argument('--template', type=str, default='audio_content_analysis',
                        help='使用的提示词模板名称（不含扩展名），默认为audio_content_analysis')
    parser.add_argument('--prompts_dir', type=str, default='prompts',
                        help='提示词模板目录，默认为prompts')
    parser.add_argument('--threads', type=int, default=1,
                        help='并发处理的线程数，默认为1')
    args = parser.parse_args()
    
    # 检查源文件夹是否存在
    if not os.path.exists(args.source_folder):
        print(f"错误：源文件夹 '{args.source_folder}' 不存在。")
        return
    
    # 创建输出文件夹
    os.makedirs(args.output, exist_ok=True)
    
    # 获取模型设置
    if args.model is None:
        # 尝试从配置中获取默认模型
        default_model = config.get_default_model()
        if default_model:
            model_path = default_model
            print(f"使用配置中的默认模型: {model_path}")
        else:
            # 如果配置中没有默认模型，则使用small
            model_path = 'small'
            print(f"未指定模型，使用默认模型: {model_path}")
    else:
        model_path = args.model
    
    # 获取API密钥
    api_key = args.api_key
    if api_key is None:
        # 尝试从配置中获取API密钥
        api_key = config.get_api_key()
        if api_key:
            print(f"使用配置中的API密钥: {api_key[:10]}...")
        else:
            # 如果配置中没有API密钥，则提示用户输入
            api_key = input("请输入DeepSeek API密钥: ").strip()
            if not api_key:
                print("错误：未提供API密钥。")
                return
    
    # 初始化转录器和总结器
    print(f"初始化Whisper转录器，模型: {model_path}")
    transcriber = WhisperTranscriber(model_path)
    
    # 如果prompts_dir是相对路径，则转换为绝对路径
    if not os.path.isabs(args.prompts_dir):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        prompts_dir = os.path.join(project_root, args.prompts_dir)
    else:
        prompts_dir = args.prompts_dir
    
    print(f"初始化DeepSeek总结器，模板: {args.template}")
    summarizer = DeepSeekSummarizer(api_key, prompts_dir)
    
    # 扫描音频文件
    print(f"扫描源文件夹: {args.source_folder}")
    audio_files = scan_audio_files(args.source_folder)
    
    if not audio_files:
        print("未找到音频文件。")
        return
    
    print(f"找到 {len(audio_files)} 个音频文件")
    
    # 创建进度队列
    progress_queue = queue.Queue()
    
    # 创建并启动工作线程
    threads = []
    max_threads = min(args.threads, len(audio_files))
    
    print(f"使用 {max_threads} 个线程进行并发处理")
    
    # 分配文件给线程
    for i in range(max_threads):
        # 每个线程处理一部分文件
        thread_files = audio_files[i::max_threads]
        
        # 创建线程
        thread = threading.Thread(
            target=process_files_thread,
            args=(thread_files, transcriber, summarizer, args.output, 
                  args.template, args.source_folder, progress_queue)
        )
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    # 监控进度
    completed = 0
    failed = 0
    file_status = {}
    
    # 初始化文件状态
    for file_path, _ in audio_files:
        file_status[file_path] = {'status': '等待中', 'progress': 0}
    
    # 显示进度
    while completed + failed < len(audio_files):
        try:
            # 从队列获取进度更新
            update = progress_queue.get(timeout=1)
            file_path = update['file']
            status = update['status']
            progress = update['progress']
            
            # 更新文件状态
            file_status[file_path]['status'] = status
            file_status[file_path]['progress'] = progress
            
            # 检查是否完成或失败
            if status == '完成':
                completed += 1
                transcript_file = update.get('transcript_file', '')
                summary_file = update.get('summary_file', '')
                # 获取相对路径用于显示
                rel_path = update.get('rel_path', os.path.basename(file_path))
                print(f"\n完成 ({completed}/{len(audio_files)}): {rel_path}")
                print(f"  转录文件: {transcript_file}")
                print(f"  总结文件: {summary_file}")
            elif status.startswith('错误'):
                failed += 1
                # 获取相对路径用于显示
                rel_path = update.get('rel_path', os.path.basename(file_path))
                print(f"\n失败 ({completed+failed}/{len(audio_files)}): {rel_path} - {status}")
            
            # 显示总体进度
            total_progress = (completed + failed) / len(audio_files) * 100
            print(f"\r总体进度: {total_progress:.1f}% ({completed+failed}/{len(audio_files)}) ", end='', flush=True)
            
        except queue.Empty:
            continue
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    print(f"\n\n处理完成！")
    print(f"成功: {completed} 个文件")
    print(f"失败: {failed} 个文件")
    print(f"输出文件夹: {args.output}")

def process_files_thread(files, transcriber, summarizer, output_folder, template, source_folder, progress_queue):
    """工作线程函数，处理分配给它的文件"""
    for file_tuple in files:
        process_audio_file(file_tuple, transcriber, summarizer, output_folder, template, source_folder, progress_queue)

if __name__ == "__main__":
    main()