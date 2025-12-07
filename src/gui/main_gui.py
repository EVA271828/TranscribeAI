#!/usr/bin/env python3
"""
音频转录与总结工具图形化界面
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter.font import Font

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.whisper_transcriber import WhisperTranscriber
from src.core.deepseek_summarizer import DeepSeekSummarizer
from src.utils.file_utils import FileUtils
from src.config.config_manager import ConfigManager


class AudioTranscriberGUI:
    """音频转录与总结工具的图形界面类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("音频转录与总结工具")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # 初始化配置管理器
        self.config = ConfigManager()
        
        # 初始化变量
        self.audio_file = tk.StringVar()
        self.model_var = tk.StringVar()
        self.api_key = tk.StringVar()
        self.template_var = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.transcription_result = tk.StringVar()
        self.summary_result = tk.StringVar()
        
        # 初始化转录器和总结器
        self.transcriber = None
        self.summarizer = None
        
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
        
        self.save_button = ttk.Button(button_frame, text="保存结果", command=self.save_results, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def setup_settings_tab(self, parent):
        """设置选项卡"""
        # 音频文件选择
        file_frame = ttk.LabelFrame(parent, text="音频文件", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Entry(file_frame, textvariable=self.audio_file, width=70).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(file_frame, text="浏览...", command=self.browse_file).pack(side=tk.RIGHT)
        
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
    
    def browse_file(self):
        """浏览选择音频文件"""
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
        if not self.audio_file.get():
            messagebox.showerror("错误", "请选择音频文件")
            return
        
        if not self.api_key.get():
            messagebox.showerror("错误", "请输入DeepSeek API密钥")
            return
        
        if not os.path.exists(self.audio_file.get()):
            messagebox.showerror("错误", "音频文件不存在")
            return
        
        # 禁用按钮
        self.start_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        
        # 清空结果
        self.transcription_text.delete(1.0, tk.END)
        self.summary_text.delete(1.0, tk.END)
        
        # 更新状态
        self.status_var.set("正在初始化模型...")
        
        # 在新线程中执行转录
        threading.Thread(target=self.transcribe_and_summarize, daemon=True).start()
    
    def transcribe_and_summarize(self):
        """转录和总结"""
        try:
            # 初始化转录器
            self.transcriber = WhisperTranscriber(self.model_var.get())
            
            # 定义进度回调函数
            def progress_callback(progress):
                # 更新状态栏显示进度
                self.root.after(0, lambda: self.status_var.set(f"正在转录音频... {progress:.1f}%"))
            
            # 转录音频（带进度回调）
            self.root.after(0, lambda: self.status_var.set("正在转录音频... 0%"))
            transcription = self.transcriber.transcribe(
                self.audio_file.get(), 
                progress_callback=progress_callback
            )
            
            # 显示转录结果
            self.root.after(0, lambda: self.transcription_text.insert(tk.END, transcription))
            
            # 初始化总结器
            self.summarizer = DeepSeekSummarizer(self.api_key.get(), "prompts")
            
            # 总结内容
            self.root.after(0, lambda: self.status_var.set("正在生成总结..."))
            audio_title = FileUtils.get_audio_title(self.audio_file.get())
            summary = self.summarizer.summarize(transcription, audio_title, self.template_var.get())
            
            # 显示总结结果
            self.root.after(0, lambda: self.summary_text.insert(tk.END, summary))
            
            # 更新状态
            self.root.after(0, lambda: self.status_var.set("转录完成"))
            
            # 启用保存按钮
            self.root.after(0, lambda: self.save_button.config(state=tk.NORMAL))
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
            self.root.after(0, lambda: self.status_var.set("错误"))
        
        finally:
            # 启用开始按钮
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
    
    def save_results(self):
        """保存结果"""
        transcription = self.transcription_text.get(1.0, tk.END).strip()
        summary = self.summary_text.get(1.0, tk.END).strip()
        
        if not transcription or not summary:
            messagebox.showerror("错误", "没有可保存的结果")
            return
        
        try:
            # 使用用户选择的输出文件夹，如果没有则使用配置中的默认值
            output_folder = self.output_folder.get() or self.config.get_output_folder()
            transcript_file, summary_file = FileUtils.save_results(
                transcription, summary, self.audio_file.get(), output_folder
            )
            messagebox.showinfo("成功", f"结果已保存:\n转录: {transcript_file}\n总结: {summary_file}")
            self.status_var.set("结果已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")


def main():
    """主程序"""
    root = tk.Tk()
    app = AudioTranscriberGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()