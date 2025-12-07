#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频音频提取工具 - GUI版本
使用FFmpeg从视频文件中提取音频，并保持源文件夹结构
"""

import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path


class AudioExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("视频音频提取工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 默认FFmpeg路径
        self.ffmpeg_path = "D:\\software\\ffmpeg-master-latest-win64-gpl-shared\\bin\\ffmpeg.exe"
        
        # 创建界面
        self.create_widgets()
        
        # 检查FFmpeg是否存在
        self.check_ffmpeg()
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # FFmpeg路径设置
        ffmpeg_frame = ttk.LabelFrame(main_frame, text="FFmpeg设置", padding="10")
        ffmpeg_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(ffmpeg_frame, text="FFmpeg路径:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.ffmpeg_path_var = tk.StringVar(value=self.ffmpeg_path)
        self.ffmpeg_path_entry = ttk.Entry(ffmpeg_frame, textvariable=self.ffmpeg_path_var, width=60)
        self.ffmpeg_path_entry.grid(row=0, column=1, sticky=tk.EW, padx=(0, 5))
        self.ffmpeg_path_entry.bind("<FocusOut>", self.on_ffmpeg_path_change)
        
        ttk.Button(ffmpeg_frame, text="浏览", command=self.browse_ffmpeg).grid(row=0, column=2)
        ffmpeg_frame.columnconfigure(1, weight=1)
        
        # 路径设置
        path_frame = ttk.LabelFrame(main_frame, text="路径设置", padding="10")
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 源文件夹
        ttk.Label(path_frame, text="源文件夹:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.source_path_var = tk.StringVar()
        self.source_path_entry = ttk.Entry(path_frame, textvariable=self.source_path_var, width=60)
        self.source_path_entry.grid(row=0, column=1, sticky=tk.EW, padx=(0, 5))
        
        ttk.Button(path_frame, text="浏览", command=self.browse_source).grid(row=0, column=2)
        
        # 目标文件夹
        ttk.Label(path_frame, text="目标文件夹:").grid(row=1, column=1, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.target_path_var = tk.StringVar()
        self.target_path_entry = ttk.Entry(path_frame, textvariable=self.target_path_var, width=60)
        self.target_path_entry.grid(row=1, column=1, sticky=tk.EW, padx=(0, 5), pady=(5, 0))
        
        ttk.Button(path_frame, text="浏览", command=self.browse_target).grid(row=1, column=2, pady=(5, 0))
        path_frame.columnconfigure(1, weight=1)
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="开始提取", command=self.start_extraction)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_extraction, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 日志文本框
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 控制线程
        self.extraction_thread = None
        self.stop_extraction_flag = False
    
    def log(self, message):
        """添加日志消息"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def check_ffmpeg(self):
        """检查FFmpeg是否存在"""
        if not os.path.exists(self.ffmpeg_path):
            self.log(f"警告: FFmpeg未找到于路径 {self.ffmpeg_path}")
            self.status_var.set("FFmpeg未找到")
            return False
        
        self.log("FFmpeg路径有效")
        self.status_var.set("就绪")
        return True
    
    def on_ffmpeg_path_change(self, event=None):
        """FFmpeg路径改变时的处理"""
        self.ffmpeg_path = self.ffmpeg_path_var.get()
        self.check_ffmpeg()
    
    def browse_ffmpeg(self):
        """浏览FFmpeg可执行文件"""
        filename = filedialog.askopenfilename(
            title="选择FFmpeg可执行文件",
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
        )
        if filename:
            self.ffmpeg_path_var.set(filename)
            self.ffmpeg_path = filename
            self.check_ffmpeg()
    
    def browse_source(self):
        """浏览源文件夹"""
        dirname = filedialog.askdirectory(title="选择源文件夹")
        if dirname:
            self.source_path_var.set(dirname)
    
    def browse_target(self):
        """浏览目标文件夹"""
        dirname = filedialog.askdirectory(title="选择目标文件夹")
        if dirname:
            self.target_path_var.set(dirname)
    
    def get_video_files(self, directory):
        """获取目录中的所有视频文件"""
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp']
        video_files = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in video_extensions):
                    video_files.append(os.path.join(root, file))
        
        return video_files
    
    def extract_audio(self, input_file, output_file):
        """使用FFmpeg提取音频"""
        # 检查输出文件是否已存在
        if os.path.exists(output_file):
            self.log(f"跳过已存在的文件: {output_file}")
            return True
        
        try:
            # 使用FFmpeg提取音频并转换为WAV格式（Whisper支持的格式）
            cmd = [
                self.ffmpeg_path,
                '-i', input_file,
                '-vn',  # 不包含视频流
                '-acodec', 'pcm_s16le',  # 音频编码为PCM 16位
                '-ar', '16000',  # 采样率16kHz（Whisper推荐）
                '-ac', '1',  # 单声道
                '-y',  # 覆盖输出文件
                output_file
            ]
            
            self.log(f"正在处理: {input_file}")
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.log(f"音频已提取: {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"处理 {input_file} 时出错: {e}")
            return False
    
    def extraction_worker(self):
        """音频提取工作线程"""
        source_dir = self.source_path_var.get()
        target_dir = self.target_path_var.get()
        
        # 检查源目录是否存在
        if not os.path.exists(source_dir):
            self.log(f"错误: 源目录不存在: {source_dir}")
            self.status_var.set("错误")
            self.enable_controls()
            return
        
        # 创建目标目录（如果不存在）
        os.makedirs(target_dir, exist_ok=True)
        
        # 获取所有视频文件
        video_files = self.get_video_files(source_dir)
        
        if not video_files:
            self.log("未找到任何视频文件")
            self.status_var.set("完成")
            self.enable_controls()
            return
        
        self.log(f"找到 {len(video_files)} 个视频文件")
        
        success_count = 0
        failure_count = 0
        
        # 处理每个视频文件
        for i, video_file in enumerate(video_files):
            # 检查是否需要停止
            if self.stop_extraction_flag:
                self.log("用户停止了处理")
                break
            
            # 更新进度
            progress = (i / len(video_files)) * 100
            self.progress_var.set(progress)
            self.status_var.set(f"处理中: {i+1}/{len(video_files)}")
            
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
            if self.extract_audio(video_file, output_file):
                success_count += 1
            else:
                failure_count += 1
        
        # 完成处理
        self.progress_var.set(100)
        self.status_var.set("完成")
        self.log(f"\n处理完成!")
        self.log(f"成功: {success_count} 个文件")
        self.log(f"失败: {failure_count} 个文件")
        
        self.enable_controls()
    
    def start_extraction(self):
        """开始音频提取"""
        # 检查FFmpeg是否存在
        if not os.path.exists(self.ffmpeg_path):
            messagebox.showerror("错误", f"FFmpeg未找到于路径 {self.ffmpeg_path}")
            return
        
        # 检查路径是否已设置
        source_dir = self.source_path_var.get()
        target_dir = self.target_path_var.get()
        
        if not source_dir or not target_dir:
            messagebox.showerror("错误", "请设置源文件夹和目标文件夹路径")
            return
        
        # 重置状态
        self.stop_extraction_flag = False
        self.progress_var.set(0)
        self.log_text.delete(1.0, tk.END)
        
        # 禁用控件
        self.disable_controls()
        
        # 启动工作线程
        self.extraction_thread = threading.Thread(target=self.extraction_worker)
        self.extraction_thread.daemon = True
        self.extraction_thread.start()
    
    def stop_extraction(self):
        """停止音频提取"""
        self.stop_extraction_flag = True
        self.status_var.set("正在停止...")
    
    def disable_controls(self):
        """禁用控件"""
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.ffmpeg_path_entry.config(state=tk.DISABLED)
        self.source_path_entry.config(state=tk.DISABLED)
        self.target_path_entry.config(state=tk.DISABLED)
    
    def enable_controls(self):
        """启用控件"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.ffmpeg_path_entry.config(state=tk.NORMAL)
        self.source_path_entry.config(state=tk.NORMAL)
        self.target_path_entry.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    app = AudioExtractorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()