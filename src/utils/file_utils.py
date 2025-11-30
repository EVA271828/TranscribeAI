import os
from datetime import datetime

class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def save_results(transcription, summary, audio_file):
        """
        保存转录和总结结果到文件
        
        Args:
            transcription (str): 语音识别的文本
            summary (str): AI生成的总结
            audio_file (str): 音频文件路径
            
        Returns:
            tuple: (转录文件路径, 总结文件路径)
        """
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 生成输出文件名
        audio_name = os.path.splitext(os.path.basename(audio_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 转录文件路径和名称
        transcript_dir = os.path.join(project_root, 'output', 'transcripts')
        os.makedirs(transcript_dir, exist_ok=True)
        transcript_file = os.path.join(transcript_dir, f"{audio_name}_转录_{timestamp}.txt")
        
        # 总结文件路径和名称
        summary_dir = os.path.join(project_root, 'output', 'summaries')
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