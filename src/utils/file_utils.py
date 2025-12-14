import os
from datetime import datetime

class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def save_results(transcription, summary, audio_file, output_folder=None, rel_path=None):
        """
        保存转录和总结结果到文件 - 支持保持源文件夹结构
        
        Args:
            transcription (str): 语音识别的文本
            summary (str): AI生成的总结
            audio_file (str): 音频文件路径
            output_folder (str, optional): 输出文件夹路径，默认为None（使用默认路径）
            rel_path (str, optional): 相对路径，用于保持源文件夹结构
            
        Returns:
            tuple: (转录文件路径, 总结文件路径)
        """
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 如果未指定输出文件夹，使用默认路径
        if output_folder is None:
            output_folder = os.path.join(project_root, 'output')
        
        # 如果输出文件夹是相对路径，则相对于项目根目录
        if not os.path.isabs(output_folder):
            output_folder = os.path.join(project_root, output_folder)
        
        # 确保输出文件夹存在
        os.makedirs(output_folder, exist_ok=True)
        
        # 生成输出文件名
        audio_name = os.path.splitext(os.path.basename(audio_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 转录文件路径和名称
        transcript_dir = os.path.join(output_folder, 'transcripts')
        # 如果有相对路径，则在转录目录下创建相同的子目录结构
        if rel_path:
            rel_dir = os.path.dirname(rel_path)
            if rel_dir:
                transcript_dir = os.path.join(transcript_dir, rel_dir)
        
        # 确保转录目录存在
        try:
            os.makedirs(transcript_dir, exist_ok=True)
        except Exception as e:
            print(f"创建转录目录失败: {transcript_dir}, 错误: {e}")
            # 如果创建子目录失败，回退到基础目录
            transcript_dir = os.path.join(output_folder, 'transcripts')
            os.makedirs(transcript_dir, exist_ok=True)
            
        transcript_file = os.path.join(transcript_dir, f"{audio_name}_转录_{timestamp}.txt")
        
        # 总结文件路径和名称
        summary_dir = os.path.join(output_folder, 'summaries')
        # 如果有相对路径，则在总结目录下创建相同的子目录结构
        if rel_path:
            rel_dir = os.path.dirname(rel_path)
            if rel_dir:
                summary_dir = os.path.join(summary_dir, rel_dir)
        
        # 确保总结目录存在
        try:
            os.makedirs(summary_dir, exist_ok=True)
        except Exception as e:
            print(f"创建总结目录失败: {summary_dir}, 错误: {e}")
            # 如果创建子目录失败，回退到基础目录
            summary_dir = os.path.join(output_folder, 'summaries')
            os.makedirs(summary_dir, exist_ok=True)
            
        summary_file = os.path.join(summary_dir, f"{audio_name}_总结_{timestamp}.md")
        
        # 保存转录文本到txt文件
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write("=" * 50 + "\n")
            f.write(f"音频文件: {audio_file}\n")
            f.write(f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(transcription)
        
        # 保存总结到md文件
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# {audio_name}\n\n")
            f.write(f"**音频文件:** {audio_file}\n\n")
            f.write(f"**处理时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## 总结内容\n\n")
            f.write(summary)
        
        print(f"转录文本已保存到: {transcript_file}")
        print(f"总结内容已保存到: {summary_file}")
        return transcript_file, summary_file
    
    @staticmethod
    def check_file_exists(file_path):
        """
        检查文件是否存在
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            bool: 文件是否存在
        """
        return os.path.exists(file_path)
    
    @staticmethod
    def get_audio_title(audio_file):
        """
        从音频文件路径获取标题
        
        Args:
            audio_file (str): 音频文件路径
            
        Returns:
            str: 音频标题
        """
        return os.path.splitext(os.path.basename(audio_file))[0]