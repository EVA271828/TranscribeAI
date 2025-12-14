#!/usr/bin/env python3
"""
音频转录与总结工具图形化界面
"""

import os
import sys
import threading
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter.font import Font
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.core.whisper_transcriber import WhisperTranscriber
from src.core.deepseek_summarizer import DeepSeekSummarizer
from src.utils.file_utils import FileUtils
from src.config.config_manager import ConfigManager


def sanitize_filename(filename):
    """清理文件名，移除或替换不安全的字符"""
    import re
    # 移除或替换不安全的字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 移除控制字符
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    # 限制长度
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200] + ext
    return filename


class AudioTranscriberGUI:
    """音频转录与总结工具的图形界面类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("音频转录与总结工具")
        self.root.geometry("900x900")
        self.root.minsize(800, 900)
        
        # 初始化配置管理器
        self.config = ConfigManager()
        
        # 初始化变量
        self.audio_file = tk.StringVar()
        self.audio_folder = tk.StringVar()
        self.model_var = tk.StringVar()
        self.api_key = tk.StringVar()
        self.template_var = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.transcription_result = tk.StringVar()
        self.summary_result = tk.StringVar()
        self.is_folder_mode = tk.BooleanVar(value=False)
        
        # 初始化转录器和总结器
        self.transcriber = None
        self.summarizer = None
        
        # 文件列表和进度跟踪
        self.audio_files = []
        self.current_file_index = 0
        self.file_progress = {}
        
        # 线程和队列管理
        self.transcription_queue = queue.Queue()
        self.summary_queue = queue.Queue()
        self.transcription_thread = None
        self.summary_thread = None
        self.stop_threads = False
        
        # 总结线程池
        self.summary_threads = []
        self.max_summary_threads = 5  # 最多支持5个并发总结线程
        self.summary_thread_pool = queue.Queue(maxsize=self.max_summary_threads)  # 限制并发数
        self.active_summary_threads = 0
        self.summary_results = {}  # 存储总结结果 {文件名: 总结内容}
        
        # 计时相关变量
        self.file_start_times = {}  # 存储每个文件的处理开始时间 {文件路径: {'transcription': 时间, 'summary': 时间}}
        
        # 设置界面
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_font = Font(size=16, weight="bold")
        title_label = ttk.Label(main_frame, text="音频转录与总结工具", font=title_font)
        title_label.pack(pady=(0, 20))
        
        # 创建选项卡
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 设置选项卡
        settings_tab = ttk.Frame(notebook)
        notebook.add(settings_tab, text="设置")
        
        # 结果选项卡
        results_tab = ttk.Frame(notebook)
        notebook.add(results_tab, text="结果")
        
        # 设置选项卡内容
        self.setup_settings_tab(settings_tab)
        
        # 结果选项卡内容
        self.setup_results_tab(results_tab)
        
        # 底部按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_button = ttk.Button(button_frame, text="开始转录", command=self.start_transcription)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_transcription, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_button = ttk.Button(button_frame, text="保存结果", command=self.save_results, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def setup_settings_tab(self, parent):
        """设置选项卡"""
        # 输入模式选择
        mode_frame = ttk.LabelFrame(parent, text="输入模式", padding="10")
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="单个文件", variable=self.is_folder_mode, value=False).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(mode_frame, text="文件夹批量处理", variable=self.is_folder_mode, value=True).pack(side=tk.LEFT)
        
        # 统一的文件/文件夹选择
        file_frame = ttk.LabelFrame(parent, text="音频文件/文件夹", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_entry = ttk.Entry(file_frame, textvariable=self.audio_file, width=70)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(file_frame, text="浏览...", command=self.browse_file_or_folder).pack(side=tk.RIGHT)
        
        # 文件列表显示（仅在文件夹模式下显示）
        self.list_frame = ttk.LabelFrame(parent, text="文件列表", padding="10")
        
        # 创建Treeview显示文件列表和进度
        columns = ("文件名", "转录状态", "转录进度", "总结状态", "总结进度")
        self.file_tree = ttk.Treeview(self.list_frame, columns=columns, show="tree headings", height=8)
        
        # 设置列标题
        self.file_tree.heading("#0", text="")
        self.file_tree.heading("文件名", text="文件名")
        self.file_tree.heading("转录状态", text="转录状态")
        self.file_tree.heading("转录进度", text="转录进度")
        self.file_tree.heading("总结状态", text="总结状态")
        self.file_tree.heading("总结进度", text="总结进度")
        
        # 设置列宽
        self.file_tree.column("#0", width=0, stretch=False)
        self.file_tree.column("文件名", width=250, minwidth=200)
        self.file_tree.column("转录状态", width=80, minwidth=60)
        self.file_tree.column("转录进度", width=80, minwidth=60)
        self.file_tree.column("总结状态", width=80, minwidth=60)
        self.file_tree.column("总结进度", width=80, minwidth=60)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 根据输入模式启用/禁用控件
        self.update_input_mode()
        
        # 绑定输入模式切换事件
        self.is_folder_mode.trace_add('write', lambda *args: self.update_input_mode())
        
        # 模型选择
        model_frame = ttk.LabelFrame(parent, text="Whisper模型", padding="10")
        model_frame.pack(fill=tk.X, pady=(0, 10))
        
        model_options = ["tiny", "base", "small", "medium", "large"]
        model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, values=model_options, state="readonly", width=20)
        model_combo.pack(side=tk.LEFT)
        model_combo.current(2)  # 默认选择"small"
        
        model_info = ttk.Label(model_frame, text="tiny(最快) ← → large(最准确)", foreground="gray")
        model_info.pack(side=tk.LEFT, padx=(10, 0))
        
        # API密钥
        api_frame = ttk.LabelFrame(parent, text="DeepSeek API密钥", padding="10")
        api_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.api_entry = ttk.Entry(api_frame, textvariable=self.api_key, show="*", width=70)
        self.api_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(api_frame, text="显示", command=self.toggle_api_visibility).pack(side=tk.RIGHT, padx=(0, 5))
        ttk.Button(api_frame, text="配置", command=self.open_config).pack(side=tk.RIGHT)
        
        # 模板选择
        template_frame = ttk.LabelFrame(parent, text="总结模板", padding="10")
        template_frame.pack(fill=tk.X, pady=(0, 10))
        
        template_options = ["audio_content_analysis", "text_summary", "meeting_analysis", "course_analysis"]
        template_combo = ttk.Combobox(template_frame, textvariable=self.template_var, values=template_options, state="readonly", width=30)
        template_combo.pack(side=tk.LEFT)
        template_combo.current(0)  # 默认选择"audio_content_analysis"
        
        template_info = ttk.Label(template_frame, text="选择适合您内容的模板", foreground="gray")
        template_info.pack(side=tk.LEFT, padx=(10, 0))
        
        # 输出文件夹选择
        output_frame = ttk.LabelFrame(parent, text="输出文件夹", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Entry(output_frame, textvariable=self.output_folder, width=70).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(output_frame, text="浏览...", command=self.browse_output_folder).pack(side=tk.RIGHT)
    
    def setup_results_tab(self, parent):
        """结果选项卡"""
        # 创建PanedWindow
        paned = ttk.PanedWindow(parent, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 转录结果
        trans_frame = ttk.LabelFrame(paned, text="转录结果", padding="10")
        paned.add(trans_frame, weight=1)
        
        self.transcription_text = scrolledtext.ScrolledText(trans_frame, wrap=tk.WORD, height=10)
        self.transcription_text.pack(fill=tk.BOTH, expand=True)
        
        # 总结结果
        summary_frame = ttk.LabelFrame(paned, text="总结结果", padding="10")
        paned.add(summary_frame, weight=1)
        
        self.summary_text = scrolledtext.ScrolledText(summary_frame, wrap=tk.WORD, height=10)
        self.summary_text.pack(fill=tk.BOTH, expand=True)
    
    def browse_file_or_folder(self):
        """根据当前模式浏览选择文件或文件夹"""
        if self.is_folder_mode.get():
            # 文件夹模式
            folder = filedialog.askdirectory(title="选择包含音频文件的文件夹")
            if folder:
                self.audio_file.set(folder)
                self.scan_and_display_audio_files()
        else:
            # 单文件模式
            filetypes = [
                ("音频文件", "*.mp3 *.wav *.m4a *.flac *.ogg"),
                ("所有文件", "*.*")
            ]
            
            filename = filedialog.askopenfilename(
                title="选择音频文件",
                filetypes=filetypes
            )
            
            if filename:
                self.audio_file.set(filename)
                # 检查断点续传状态
                self.check_single_file_resume_status(filename)
    
    def check_single_file_resume_status(self, audio_file):
        """检查单个文件的断点续传状态"""
        # 获取输出文件夹
        output_folder = self.output_folder.get() or self.config.get_output_folder()
        transcript_dir = os.path.join(output_folder, 'transcripts')
        summary_dir = os.path.join(output_folder, 'summaries')
        
        # 获取文件基本信息
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        trans_status = '等待'
        trans_progress = '0%'
        sum_status = '等待'
        sum_progress = '0%'
        
        # 检查转录文件
        if os.path.exists(transcript_dir):
            for trans_filename in os.listdir(transcript_dir):
                if trans_filename.startswith(f"{base_name}_转录_") and trans_filename.endswith(".txt"):
                    trans_status = '转录完成(已存在)'
                    trans_progress = '100%'
                    break
        
        # 检查总结文件
        if os.path.exists(summary_dir):
            for sum_filename in os.listdir(summary_dir):
                if sum_filename.startswith(f"{base_name}_总结") and sum_filename.endswith(".md"):
                    potential_file = os.path.join(summary_dir, sum_filename)
                    try:
                        with open(potential_file, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                        if content:
                            summary = content
                            sum_status = '总结完成(已存在)'
                            sum_progress = '100%'
                            break
                    except Exception:
                        continue
        
        # 更新状态显示
        status_text = f"文件状态: 转录{trans_status}, 总结{sum_status}"
        self.status_var.set(status_text)
        
        # 如果转录和总结都已完成，提示用户
        if trans_progress == '100%' and sum_progress == '100%':
            # 尝试加载已存在的文件
            self.load_existing_files(audio_file, base_name, transcript_dir, summary_dir)
    
    def load_existing_files(self, audio_file, base_name, transcript_dir, summary_dir):
        """加载已存在的转录和总结文件"""
        transcription = None
        summary = None
        transcript_file = None
        
        # 查找并加载转录文件
        if os.path.exists(transcript_dir):
            for trans_filename in os.listdir(transcript_dir):
                if trans_filename.startswith(f"{base_name}_转录_") and trans_filename.endswith(".txt"):
                    potential_file = os.path.join(transcript_dir, trans_filename)
                    try:
                        with open(potential_file, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                        if content:
                            transcription = content
                            transcript_file = potential_file
                            break
                    except Exception:
                        continue
        
        # 查找并加载总结文件
        if os.path.exists(summary_dir):
            for sum_filename in os.listdir(summary_dir):
                if sum_filename.startswith(f"{base_name}_总结") and sum_filename.endswith(".md"):
                    potential_file = os.path.join(summary_dir, sum_filename)
                    try:
                        with open(potential_file, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                        if content:
                            summary = content
                            break
                    except Exception:
                        continue
        
        # 显示加载的内容
        if transcription:
            self.transcription_text.delete(1.0, tk.END)
            self.transcription_text.insert(tk.END, transcription)
        
        if summary:
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(tk.END, summary)
        
        # 更新状态
        status = "已加载现有文件"
        if transcript_file:
            status += f" | 转录文件: {os.path.basename(transcript_file)}"
        self.status_var.set(status)
        
        # 启用保存按钮
        self.save_button.config(state=tk.NORMAL)
    
    def scan_audio_files(self, source_folder):
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
    
    def scan_and_display_audio_files(self):
        """扫描文件夹中的音频文件（包括嵌套子文件夹）并显示在UI中"""
        folder = self.audio_file.get()
        if not folder or not os.path.exists(folder):
            return
        
        # 清空文件列表
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        self.audio_files = []
        self.file_progress = {}
        
        # 获取音频文件列表
        audio_files = self.scan_audio_files(folder)
        
        # 获取输出文件夹
        output_folder = self.output_folder.get() or self.config.get_output_folder()
        transcript_dir = os.path.join(output_folder, 'transcripts')
        summary_dir = os.path.join(output_folder, 'summaries')
        
        # 处理每个音频文件
        for file_path, rel_path in audio_files:
            self.audio_files.append((file_path, rel_path))
            
            # 检查转录和总结文件是否已存在
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            trans_status = '等待'
            trans_progress = '0%'
            sum_status = '等待'
            sum_progress = '0%'
            
            # 检查转录文件
            if os.path.exists(transcript_dir):
                # 构建转录子目录路径
                trans_subdir = transcript_dir
                rel_dir = os.path.dirname(rel_path)
                if rel_dir:
                    trans_subdir = os.path.join(transcript_dir, rel_dir)
                
                if os.path.exists(trans_subdir):
                    for trans_filename in os.listdir(trans_subdir):
                        if trans_filename.startswith(f"{base_name}_转录_") and trans_filename.endswith(".txt"):
                            trans_status = '转录完成(已存在)'
                            trans_progress = '100%'
                            break
            
            # 检查总结文件
            if os.path.exists(summary_dir):
                # 构建总结子目录路径
                sum_subdir = summary_dir
                rel_dir = os.path.dirname(rel_path)
                if rel_dir:
                    sum_subdir = os.path.join(summary_dir, rel_dir)
                
                if os.path.exists(sum_subdir):
                    for sum_filename in os.listdir(sum_subdir):
                        if sum_filename.startswith(f"{base_name}_总结") and sum_filename.endswith(".md"):
                            sum_status = '总结完成(已存在)'
                            sum_progress = '100%'
                            break
            
            # 添加到进度字典
            self.file_progress[file_path] = {
                'trans_status': trans_status,
                'trans_progress': int(trans_progress.rstrip('%')),
                'sum_status': sum_status,
                'sum_progress': int(sum_progress.rstrip('%')),
                'rel_path': rel_path  # 存储相对路径
            }
            
            # 添加到树形视图，显示相对路径
            display_name = rel_path if rel_path != os.path.basename(file_path) else os.path.basename(file_path)
            self.file_tree.insert('', 'end', values=(display_name, trans_status, trans_progress, sum_status, sum_progress))
        
        if not self.audio_files:
            messagebox.showinfo("提示", "所选文件夹中没有找到音频文件")
    
    def update_input_mode(self):
        """根据输入模式更新界面"""
        is_folder = self.is_folder_mode.get()
        
        # 更新标签文本
        if is_folder:
            # 文件夹模式
            for widget in self.file_entry.master.winfo_children():
                if isinstance(widget, ttk.LabelFrame):
                    widget.config(text="音频文件夹")
                    break
            
            # 显示文件列表
            self.list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10), after=self.file_entry.master)
        else:
            # 单文件模式
            for widget in self.file_entry.master.winfo_children():
                if isinstance(widget, ttk.LabelFrame):
                    widget.config(text="音频文件")
                    break
            
            # 隐藏文件列表
            self.list_frame.pack_forget()
            
            # 检查当前选择的文件是否存在断点续传的可能
            current_file = self.audio_file.get()
            if current_file and os.path.exists(current_file):
                self.check_single_file_resume_status(current_file)
    
    def update_file_progress(self, file_path, status, progress, stage="transcription"):
        """更新文件处理进度
        stage: "transcription" 或 "summary"
        """
        if file_path in self.file_progress:
            # 计算耗时
            elapsed_time = ""
            if file_path in self.file_start_times and stage in self.file_start_times[file_path]:
                start_time = self.file_start_times[file_path][stage]
                current_time = datetime.now()
                elapsed_seconds = (current_time - start_time).total_seconds()
                # 格式化为分:秒
                minutes = int(elapsed_seconds // 60)
                seconds = int(elapsed_seconds % 60)
                elapsed_time = f" ({minutes:02d}:{seconds:02d})"
            
            # 更新进度字典
            if stage == "transcription":
                self.file_progress[file_path]['trans_status'] = status
                self.file_progress[file_path]['trans_progress'] = progress
            else:  # summary
                self.file_progress[file_path]['sum_status'] = status
                self.file_progress[file_path]['sum_progress'] = progress
            
            # 更新树形视图中的显示
            for item in self.file_tree.get_children():
                values = self.file_tree.item(item, 'values')
                if values and values[0] == os.path.basename(file_path):
                    # 获取当前值
                    filename = values[0]
                    trans_status = values[1] if stage == "summary" else status + elapsed_time
                    trans_progress = values[2] if stage == "summary" else f"{progress}%"
                    sum_status = values[3] if stage == "transcription" else status + elapsed_time
                    sum_progress = values[4] if stage == "transcription" else f"{progress}%"
                    
                    # 更新整行
                    self.file_tree.item(item, values=(filename, trans_status, trans_progress, sum_status, sum_progress))
                    break
                elif values and file_path in self.file_progress and values[0] == self.file_progress[file_path].get('rel_path', os.path.basename(file_path)):
                    # 如果相对路径匹配，也进行更新
                    filename = values[0]
                    trans_status = values[1] if stage == "summary" else status + elapsed_time
                    trans_progress = values[2] if stage == "summary" else f"{progress}%"
                    sum_status = values[3] if stage == "transcription" else status + elapsed_time
                    sum_progress = values[4] if stage == "transcription" else f"{progress}%"
                    
                    # 更新整行
                    self.file_tree.item(item, values=(filename, trans_status, trans_progress, sum_status, sum_progress))
                    break
    
    def browse_output_folder(self):
        """浏览选择输出文件夹"""
        folder = filedialog.askdirectory(title="选择输出文件夹")
        if folder:
            self.output_folder.set(folder)
    
    def toggle_api_visibility(self):
        """切换API密钥可见性"""
        if self.api_entry.cget("show") == "*":
            self.api_entry.config(show="")
        else:
            self.api_entry.config(show="*")
    
    def open_config(self):
        """打开配置窗口"""
        config_window = tk.Toplevel(self.root)
        config_window.title("配置设置")
        config_window.geometry("500x400")
        config_window.transient(self.root)
        config_window.grab_set()
        
        # 创建配置界面
        notebook = ttk.Notebook(config_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # API密钥配置
        api_tab = ttk.Frame(notebook)
        notebook.add(api_tab, text="API密钥")
        
        ttk.Label(api_tab, text="DeepSeek API密钥:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        api_entry = ttk.Entry(api_tab, show="*", width=60)
        api_entry.pack(fill=tk.X, padx=10, pady=5)
        api_entry.insert(0, self.config.get_api_key() or "")
        
        # 模型配置
        model_tab = ttk.Frame(notebook)
        notebook.add(model_tab, text="默认模型")
        
        ttk.Label(model_tab, text="选择默认Whisper模型:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        
        model_var = tk.StringVar()
        model_var.set(self.config.get_default_model() or "small")
        
        for i, model in enumerate(["tiny", "base", "small", "medium", "large"]):
            ttk.Radiobutton(
                model_tab, 
                text=f"{model} - {'最快' if model == 'tiny' else '最准确' if model == 'large' else '中等'}",
                variable=model_var, 
                value=model
            ).pack(anchor=tk.W, padx=20, pady=5)
        
        # 模板配置
        template_tab = ttk.Frame(notebook)
        notebook.add(template_tab, text="默认模板")
        
        ttk.Label(template_tab, text="选择默认总结模板:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        
        template_var = tk.StringVar()
        template_var.set(self.config.get_default_template() or "audio_content_analysis")
        
        templates = [
            ("audio_content_analysis", "音频内容深度分析"),
            ("text_summary", "通用文本摘要"),
            ("meeting_analysis", "会议记录分析"),
            ("course_analysis", "课程内容分析")
        ]
        
        for template, desc in templates:
            ttk.Radiobutton(
                template_tab, 
                text=f"{template} - {desc}",
                variable=template_var, 
                value=template
            ).pack(anchor=tk.W, padx=20, pady=5)
        
        # 输出文件夹配置
        output_tab = ttk.Frame(notebook)
        notebook.add(output_tab, text="输出文件夹")
        
        ttk.Label(output_tab, text="选择默认输出文件夹:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        
        output_var = tk.StringVar()
        output_var.set(self.config.get_output_folder() or "output")
        
        output_frame = ttk.Frame(output_tab)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        output_entry = ttk.Entry(output_frame, textvariable=output_var, width=50)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        def browse_output():
            folder = filedialog.askdirectory(title="选择输出文件夹")
            if folder:
                output_var.set(folder)
        
        ttk.Button(output_frame, text="浏览...", command=browse_output).pack(side=tk.RIGHT)
        
        # 按钮区域
        button_frame = ttk.Frame(config_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_config():
            self.config.set_api_key(api_entry.get())
            self.config.set_default_model(model_var.get())
            self.config.set_default_template(template_var.get())
            self.config.set_output_folder(output_var.get())
            self.load_config()
            messagebox.showinfo("成功", "配置已保存")
            config_window.destroy()
        
        ttk.Button(button_frame, text="保存", command=save_config).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="取消", command=config_window.destroy).pack(side=tk.RIGHT)
    
    def load_config(self):
        """加载配置"""
        api_key = self.config.get_api_key()
        if api_key:
            self.api_key.set(api_key)
        
        default_model = self.config.get_default_model()
        if default_model:
            self.model_var.set(default_model)
        
        default_template = self.config.get_default_template()
        if default_template:
            self.template_var.set(default_template)
        
        output_folder = self.config.get_output_folder()
        if output_folder:
            self.output_folder.set(output_folder)
    
    def start_transcription(self):
        """开始转录"""
        # 验证输入
        if self.is_folder_mode.get():
            # 文件夹模式
            folder = self.audio_file.get()
            if not folder:
                messagebox.showerror("错误", "请选择音频文件夹")
                return
            
            if not os.path.exists(folder):
                messagebox.showerror("错误", "所选文件夹不存在")
                return
            
            if not self.audio_files:
                messagebox.showerror("错误", "文件夹中没有音频文件")
                return
        else:
            # 单文件模式
            file_path = self.audio_file.get()
            if not file_path:
                messagebox.showerror("错误", "请选择音频文件")
                return
            
            if not os.path.exists(file_path):
                messagebox.showerror("错误", "所选文件不存在")
                return
        
        if not self.api_key.get():
            messagebox.showerror("错误", "请输入DeepSeek API密钥")
            return
        
        # 禁用按钮
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.DISABLED)
        
        # 在文件夹模式下清空结果，单文件模式下不清空（支持断点续传）
        if self.is_folder_mode.get():
            self.transcription_text.delete(1.0, tk.END)
            self.summary_text.delete(1.0, tk.END)
        
        # 重置进度
        if self.is_folder_mode.get():
            for file_path in self.audio_files:
                self.update_file_progress(file_path, '等待', 0, "transcription")
                self.update_file_progress(file_path, '等待', 0, "summary")
        
        # 更新状态
        self.status_var.set("正在初始化模型...")
        
        # 在新线程中执行转录
        threading.Thread(target=self.transcribe_and_summarize, daemon=True).start()
    
    def transcribe_and_summarize(self):
        """转录和总结 - 使用双线程处理"""
        try:
            # 重置停止标志
            self.stop_threads = False
            
            # 清空队列
            while not self.transcription_queue.empty():
                self.transcription_queue.get()
            while not self.summary_queue.empty():
                self.summary_queue.get()
            
            # 清空线程池
            self.summary_threads.clear()
            self.active_summary_threads = 0
            
            # 初始化转录器和总结器
            self.transcriber = WhisperTranscriber(self.model_var.get())
            # 使用绝对路径指向prompts目录
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            prompts_dir = os.path.join(project_root, "prompts")
            self.summarizer = DeepSeekSummarizer(self.api_key.get(), prompts_dir)
            
            # 更新状态栏，表示模型初始化完成
            self.root.after(0, lambda: self.status_var.set("模型初始化完成，准备开始转录..."))
            
            # 根据模式选择处理方式
            if self.is_folder_mode.get():
                # 文件夹模式 - 批量处理
                for audio_file_tuple in self.audio_files:
                    self.transcription_queue.put(audio_file_tuple)
            else:
                # 单文件模式
                self.transcription_queue.put((self.audio_file.get(), os.path.basename(self.audio_file.get())))
            
            # 启动转录线程（CPU密集型）
            self.transcription_thread = threading.Thread(target=self.transcription_worker, daemon=True)
            self.transcription_thread.start()
            
            # 启动多个总结线程（I/O密集型）
            # 不预先启动线程，而是在有任务时动态创建
            self.active_summary_threads = 0
            
            # 监控线程状态
            self.monitor_threads()
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
            self.root.after(0, lambda: self.status_var.set("错误"))
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
    
    def transcription_worker(self):
        """转录工作线程 - 处理CPU密集型任务"""
        while not self.stop_threads and not self.transcription_queue.empty():
            try:
                # 从队列获取文件（现在是元组：(完整路径, 相对路径)）
                audio_file_tuple = self.transcription_queue.get(timeout=1)
                audio_file = audio_file_tuple[0]  # 完整路径
                rel_path = audio_file_tuple[1]    # 相对路径
                
                # 记录转录开始时间
                if audio_file not in self.file_start_times:
                    self.file_start_times[audio_file] = {}
                self.file_start_times[audio_file]['transcription'] = datetime.now()
                
                # 检查转录文件是否已存在
                output_folder = self.output_folder.get() or self.config.get_output_folder()
                base_name = os.path.splitext(os.path.basename(audio_file))[0]
                
                # 查找最新的转录文件
                transcript_dir = os.path.join(output_folder, 'transcripts')
                transcript_file = None
                transcription = None
                
                if os.path.exists(transcript_dir):
                    # 查找匹配的转录文件
                    for filename in os.listdir(transcript_dir):
                        if filename.startswith(f"{base_name}_转录_") and filename.endswith(".txt"):
                            potential_file = os.path.join(transcript_dir, filename)
                            # 如果找到了文件，读取其内容
                            try:
                                with open(potential_file, 'r', encoding='utf-8') as f:
                                    transcription = f.read().strip()
                                if transcription:  # 确保文件不为空
                                    transcript_file = potential_file
                                    break
                            except Exception:
                                continue
                
                if transcript_file and transcription:
                    # 转录文件已存在，跳过转录步骤
                    self.root.after(0, self.update_file_progress, audio_file, '转录完成(已存在)', 100, "transcription")
                    
                    # 将结果放入总结队列
                    self.summary_queue.put({
                        'audio_file': audio_file,
                        'rel_path': rel_path,
                        'transcription': transcription,
                        'transcript_file': transcript_file
                    })
                    
                    # 动态创建总结线程（如果未达到最大线程数）
                    if self.active_summary_threads < self.max_summary_threads:
                        summary_thread = threading.Thread(target=self.summary_worker, daemon=True)
                        summary_thread.start()
                        self.summary_threads.append(summary_thread)
                        self.active_summary_threads += 1
                else:
                    # 需要进行转录
                    # 更新状态
                    self.root.after(0, self.update_file_progress, audio_file, '转录中', 0, "transcription")
                    
                    # 定义进度回调函数
                    def progress_callback(progress):
                        # 更新文件进度
                        self.root.after(0, self.update_file_progress, audio_file, '转录中', progress, "transcription")
                    
                    # 转录音频
                    def status_callback(status):
                        # 更新状态栏
                        self.root.after(0, self.status_var.set, status)
                    
                    transcription = self.transcriber.transcribe(
                        audio_file, 
                        progress_callback=progress_callback,
                        status_callback=status_callback
                    )
                    
                    # 立即保存转录文件
                    
                    # 获取输出文件夹
                    output_folder = self.output_folder.get() or self.config.get_output_folder()
                    
                    # 创建转录目录
                    transcript_dir = os.path.join(output_folder, 'transcripts')
                    
                    # 获取相对路径的目录部分
                    rel_dir = os.path.dirname(rel_path)
                    
                    # 如果有相对路径的目录部分，则在转录目录下创建相同的子目录结构
                    if rel_dir:
                        transcript_dir = os.path.join(transcript_dir, rel_dir)
                    
                    os.makedirs(transcript_dir, exist_ok=True)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    transcript_file = os.path.join(transcript_dir, f"{safe_base_name}_转录_{timestamp}.txt")
                    
                    # 保存转录文本
                    with open(transcript_file, 'w', encoding='utf-8') as f:
                        f.write(transcription)
                    
                    # 更新状态为转录完成
                    self.root.after(0, self.update_file_progress, audio_file, '转录完成', 100, "transcription")
                    
                    # 将结果放入总结队列
                    self.summary_queue.put({
                        'audio_file': audio_file,
                        'rel_path': rel_path,
                        'transcription': transcription,
                        'transcript_file': transcript_file
                    })
                    
                    # 动态创建总结线程（如果未达到最大线程数）
                    if self.active_summary_threads < self.max_summary_threads:
                        summary_thread = threading.Thread(target=self.summary_worker, daemon=True)
                        summary_thread.start()
                        self.summary_threads.append(summary_thread)
                        self.active_summary_threads += 1
                
            except queue.Empty:
                continue
            except Exception as e:
                # 更新状态为错误
                self.root.after(0, self.update_file_progress, audio_file, f'错误: {str(e)}', 0, "transcription")
                print(f"转录文件 {audio_file} 时出错: {str(e)}")
    
    def summary_worker(self):
        """总结工作线程 - 处理I/O密集型任务"""
        while not self.stop_threads:
            try:
                # 从队列获取转录结果
                item = self.summary_queue.get(timeout=1)
                audio_file = item['audio_file']
                rel_path = item['rel_path']  # 获取相对路径
                transcription = item['transcription']
                transcript_file = item.get('transcript_file', '')
                
                # 记录总结开始时间
                if audio_file not in self.file_start_times:
                    self.file_start_times[audio_file] = {}
                self.file_start_times[audio_file]['summary'] = datetime.now()
                
                # 检查总结文件是否已存在
                output_folder = self.output_folder.get() or self.config.get_output_folder()
                base_name = os.path.splitext(os.path.basename(audio_file))[0]
                
                # 获取输出文件夹
                output_folder = self.output_folder.get() or self.config.get_output_folder()
                
                # 创建总结目录
                summary_dir = os.path.join(output_folder, 'summaries')
                
                # 获取相对路径的目录部分
                rel_dir = os.path.dirname(rel_path)
                
                # 如果有相对路径的目录部分，则在总结目录下创建相同的子目录结构
                if rel_dir:
                    summary_dir = os.path.join(summary_dir, rel_dir)
                
                summary_file = None
                summary = None
                
                if os.path.exists(summary_dir):
                    # 查找匹配的总结文件
                    for filename in os.listdir(summary_dir):
                        if filename.startswith(f"{base_name}_总结") and filename.endswith(".md"):
                            potential_file = os.path.join(summary_dir, filename)
                            try:
                                with open(potential_file, 'r', encoding='utf-8') as f:
                                    summary = f.read().strip()
                                if summary:  # 确保文件不为空
                                    summary_file = potential_file
                                    break
                            except Exception:
                                continue
                
                if summary_file and summary:
                    # 总结文件已存在，跳过总结步骤
                    self.root.after(0, self.update_file_progress, audio_file, '总结完成(已存在)', 100, "summary")
                    
                    # 处理结果
                    if self.is_folder_mode.get():
                        self._save_batch_result(audio_file, rel_path, transcription, summary, transcript_file)
                    else:
                        self._display_single_result(audio_file, transcription, summary, transcript_file, rel_path)
                else:
                    # 需要进行总结
                    # 更新状态
                    status_text = f'总结中 ({os.path.basename(transcript_file) if transcript_file else ""})'
                    self.root.after(0, self.update_file_progress, audio_file, status_text, 0, "summary")
                    
                    # 生成总结
                    audio_title = FileUtils.get_audio_title(audio_file)
                    summary = self.summarizer.summarize(transcription, audio_title, self.template_var.get())
                    
                    # 处理结果
                    if self.is_folder_mode.get():
                        self._save_batch_result(audio_file, rel_path, transcription, summary, transcript_file)
                    else:
                        self._display_single_result(audio_file, transcription, summary, transcript_file, rel_path)
                
                # 从线程池中移除当前线程
                try:
                    self.summary_thread_pool.get_nowait()
                except queue.Empty:
                    pass
                
                # 减少活跃线程计数
                self.active_summary_threads -= 1
                
            except queue.Empty:
                continue
            except Exception as e:
                self.root.after(0, self.update_file_progress, audio_file, f'错误: {str(e)}', 0, "summary")
                print(f"总结文件 {audio_file} 时出错: {str(e)}")
                
                # 从线程池中移除当前线程
                try:
                    self.summary_thread_pool.get_nowait()
                except queue.Empty:
                    pass
                
                # 减少活跃线程计数
                self.active_summary_threads -= 1
    
    def _save_batch_result(self, audio_file, rel_path, transcription, summary, transcript_file):
        """保存批量处理结果 - 保持源文件夹结构"""
        # 创建保持源文件夹结构的输出路径
        # 获取相对路径的目录部分
        rel_dir = os.path.dirname(rel_path)
        
        # 获取输出文件夹
        output_folder = self.output_folder.get() or self.config.get_output_folder()
        
        # 检查总结文件是否已存在
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        summary_dir = os.path.join(output_folder, 'summaries')
        # 如果有相对路径的目录部分，则在总结目录下创建相同的子目录结构
        if rel_dir:
            summary_dir = os.path.join(summary_dir, rel_dir)
        
        summary_exists = False
        
        if os.path.exists(summary_dir):
            for filename in os.listdir(summary_dir):
                if filename.startswith(f"{base_name}_总结") and filename.endswith(".md"):
                    summary_exists = True
                    break
        
        if not summary_exists:
            # 只保存总结文件
            summary_file = self._save_summary_only(audio_file, summary, output_folder, rel_path)
            status_text = f'完成 (转录:{os.path.basename(transcript_file) if transcript_file else "无"}, 总结:{os.path.basename(summary_file)})'
        else:
            # 总结文件已存在
            status_text = f'完成 (转录:{os.path.basename(transcript_file) if transcript_file else "无"}, 总结:已存在)'
        
        self.root.after(0, self.update_file_progress, audio_file, '总结完成', 100, "summary")
    
    def _save_summary_only(self, audio_file, summary, output_folder, rel_path=None):
        """只保存总结文件 - 保持源文件夹结构"""
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 创建保持源文件夹结构的输出路径
        summary_dir = os.path.normpath(os.path.join(output_folder, 'summaries'))
        
        # 如果有相对路径，则在总结目录下创建相同的子目录结构
        if rel_path:
            rel_dir = os.path.dirname(rel_path)
            if rel_dir:
                summary_dir = os.path.normpath(os.path.join(summary_dir, rel_dir))
        
        # 保存总结文本 - 修改为.md格式
        safe_base_name = sanitize_filename(base_name)
        summary_file = os.path.normpath(os.path.join(summary_dir, f"{safe_base_name}_总结.md"))
        with open(summary_file, 'w', encoding='utf-8') as f:
            # 使用Markdown格式
            f.write(f"# {base_name}\n\n")
            f.write(f"**音频文件:** {audio_file}\n\n")
            f.write(f"**处理时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## 总结内容\n\n")
            f.write(summary)
        
        # 更新进度字典中的文件状态
        if audio_file in self.file_progress:
            self.file_progress[audio_file]['sum_status'] = '总结完成'
            self.file_progress[audio_file]['sum_progress'] = 100
        
        # 更新树形视图
        for item in self.file_tree.get_children():
            values = self.file_tree.item(item, 'values')
            if values and values[0] == self.file_progress[audio_file].get('rel_path', os.path.basename(audio_file)):
                self.file_tree.item(item, values=(
                    values[0], values[1], values[2], '总结完成', '100%'
                ))
                break
        
        return summary_file
    
    def _display_single_result(self, audio_file, transcription, summary, transcript_file, rel_path=None):
        """显示单文件结果"""
        # 在文件夹模式下清空结果，单文件模式下不清空（支持断点续传）
        if self.is_folder_mode.get():
            self.root.after(0, lambda: self.transcription_text.delete(1.0, tk.END))
            self.root.after(0, lambda: self.summary_text.delete(1.0, tk.END))
        
        # 显示结果在界面上
        self.root.after(0, lambda t=transcription: self.transcription_text.insert(tk.END, t))
        self.root.after(0, lambda s=summary: self.summary_text.insert(tk.END, s))
        
        # 显示转录文件路径
        if transcript_file and os.path.exists(transcript_file):
            self.root.after(0, lambda: self.status_var.set(f"转录已保存到: {transcript_file}"))
        
        # 检查是否需要保存总结文件
        output_folder = self.output_folder.get() or self.config.get_output_folder()
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        summary_dir = os.path.join(output_folder, 'summaries')
        summary_exists = False
        
        if os.path.exists(summary_dir):
            for filename in os.listdir(summary_dir):
                if filename.startswith(f"{base_name}_总结") and filename.endswith(".md"):
                    summary_exists = True
                    break
        
        if not summary_exists:
            # 保存总结文件
            self._save_summary_only(audio_file, summary, output_folder, rel_path)
            self.root.after(0, lambda: self.status_var.set(f"转录已保存到: {transcript_file}, 总结已保存"))
        else:
            self.root.after(0, lambda: self.status_var.set(f"转录已保存到: {transcript_file}, 总结已存在"))
        
        self.root.after(0, self.update_file_progress, audio_file, '总结完成', 100, "summary")
    
    def monitor_threads(self):
        """监控线程状态"""
        def check_threads():
            # 检查转录线程
            if self.transcription_thread and not self.transcription_thread.is_alive():
                self.transcription_thread = None
            
            # 检查总结线程
            active_threads = []
            for thread in self.summary_threads:
                if thread.is_alive():
                    active_threads.append(thread)
            self.summary_threads = active_threads
            
            # 如果所有线程都完成，更新状态
            if (self.transcription_thread is None and 
                len(self.summary_threads) == 0 and 
                self.transcription_queue.empty() and 
                self.summary_queue.empty()):
                
                self.status_var.set("处理完成")
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
                self.save_button.config(state=tk.NORMAL)
                
                # 显示完成消息
                if self.is_folder_mode.get():
                    completed_count = sum(1 for status in self.file_progress.values() 
                                        if status.get('trans_status', '').startswith('转录完成') and 
                                           status.get('sum_status', '').startswith('总结完成'))
                    total_count = len(self.audio_files)
                    self.root.after(0, lambda: messagebox.showinfo(
                        "批量处理完成", 
                        f"已完成 {completed_count}/{total_count} 个文件的处理"
                    ))
                else:
                    self.root.after(0, lambda: messagebox.showinfo("处理完成", "音频转录与总结已完成"))
            else:
                # 继续监控
                self.root.after(1000, check_threads)
        
        # 开始监控
        self.root.after(1000, check_threads)
    
    def stop_transcription(self):
        """停止转录过程"""
        self.stop_threads = True
        self.status_var.set("正在停止...")
        self.stop_button.config(state=tk.DISABLED)
        
        # 通知转录器停止（如果支持）
        if self.transcriber and hasattr(self.transcriber, 'stop'):
            self.transcriber.stop()
            
        # 通知总结器停止（如果支持）
        if self.summarizer and hasattr(self.summarizer, 'stop'):
            self.summarizer.stop()
        
        # 等待所有线程结束，增加超时时间
        if self.transcription_thread and self.transcription_thread.is_alive():
            self.transcription_thread.join(timeout=5)
        
        # 等待所有总结线程结束，增加超时时间
        for thread in self.summary_threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        # 清空队列
        while not self.transcription_queue.empty():
            try:
                self.transcription_queue.get_nowait()
            except queue.Empty:
                break
                
        while not self.summary_queue.empty():
            try:
                self.summary_queue.get_nowait()
            except queue.Empty:
                break
        
        # 重置状态
        self.stop_threads = False
        self.transcription_thread = None
        self.summary_threads = []
        self.active_summary_threads = 0
        
        # 重置转录器和总结器的停止标志
        if self.transcriber and hasattr(self.transcriber, 'reset_stop_flag'):
            self.transcriber.reset_stop_flag()
            
        if self.summarizer and hasattr(self.summarizer, 'reset_stop_flag'):
            self.summarizer.reset_stop_flag()
        
        # 更新UI状态
        self.status_var.set("已停止")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # 更新所有未完成文件的状态为"已停止"
        for file_path, progress_info in self.file_progress.items():
            if progress_info['trans_progress'] < 100:
                self.update_file_progress(file_path, '已停止', 0, "transcription")
            if progress_info['sum_progress'] < 100:
                self.update_file_progress(file_path, '已停止', 0, "summary")
        
        # 重置线程相关变量
        self.transcription_thread = None
        self.summary_threads = []
        self.active_summary_threads = 0
        
        # 重置计时变量
        self.file_start_times = {}
    
    def save_results(self, audio_file=None, transcription=None, summary=None, rel_path=None):
        """保存转录和总结结果"""
        # 如果传入了参数，使用传入的参数保存单个文件的结果
        if audio_file and transcription is not None and summary is not None:
            output_folder = self.output_folder.get() or self.config.get_output_folder()
            
            # 保存结果，保持源文件夹结构
            transcript_file, summary_file = FileUtils.save_results(
                transcription, summary, audio_file, output_folder, rel_path
            )
            
            # 显示保存位置
            messagebox.showinfo(
                "保存完成",
                f"转录文件: {transcript_file}\n总结文件: {summary_file}"
            )
            return
        
        # 批量处理模式下，结果已经自动保存
        if self.is_folder_mode.get() and self.audio_files:
            output_dir = self.config.get_output_folder() or 'output'
            # 确保路径使用正确的分隔符
            transcript_dir = os.path.normpath(os.path.join(output_dir, 'transcripts'))
            summary_dir = os.path.normpath(os.path.join(output_dir, 'summaries'))
            messagebox.showinfo(
                "保存结果",
                f"批量处理结果已保存到以下目录：\n\n"
                f"转录文件: {transcript_dir}\n"
                f"总结文件: {summary_dir}"
            )
            self.status_var.set("结果已保存")
            return
        
        # 单文件模式下的保存逻辑
        transcription = self.transcription_text.get(1.0, tk.END).strip()
        summary = self.summary_text.get(1.0, tk.END).strip()
        
        if not transcription and not summary:
            messagebox.showwarning("警告", "没有可保存的内容")
            return
        
        try:
            # 使用用户选择的输出文件夹，如果没有则使用配置中的默认值
            output_dir = self.output_folder.get() or self.config.get_output_folder() or 'output'
            
            # 规范化路径并确保输出文件夹存在
            output_dir = os.path.normpath(output_dir)
            os.makedirs(output_dir, exist_ok=True)
            
            # 获取音频文件名（不含扩展名）作为基础文件名
            file_path = self.audio_file.get()
            if not file_path:
                raise ValueError("未选择音频文件")
            
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # 保存转录文本
            safe_base_name = sanitize_filename(base_name)
            transcript_file = os.path.normpath(os.path.join(output_dir, f"{safe_base_name}_transcript.txt"))
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(transcription)
            
            # 保存总结文本 - 修改为.md格式
            safe_base_name = sanitize_filename(base_name)
            summary_file = os.path.normpath(os.path.join(output_dir, f"{safe_base_name}_总结.md"))
            with open(summary_file, 'w', encoding='utf-8') as f:
                # 使用Markdown格式
                f.write(f"# {base_name}\n\n")
                f.write(f"**音频文件:** {file_path}\n\n")
                f.write(f"**处理时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("## 总结内容\n\n")
                f.write(summary)
            
            messagebox.showinfo("保存成功", f"结果已保存:\n转录: {transcript_file}\n总结: {summary_file}")
            self.status_var.set("结果已保存")
        except Exception as e:
            messagebox.showerror("保存失败", f"保存结果时出错: {str(e)}")


def main():
    """主程序"""
    root = tk.Tk()
    app = AudioTranscriberGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()