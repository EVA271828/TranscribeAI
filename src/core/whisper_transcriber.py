import whisper
import torch
import time
import os

class WhisperTranscriber:
    """Whisper语音识别类"""
    
    def __init__(self, model_name="small"):
        """
        初始化Whisper模型
        
        Args:
            model_name (str): 模型名称，可选: tiny, base, small, medium, large
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_name
        self.model = None
        print(f"设备设置为使用 {self.device}")
    
    def load_model(self):
        """加载Whisper模型"""
        if self.model is None:
            print(f"正在加载模型: {self.model_name}")
            start_time = time.time()
            self.model = whisper.load_model(self.model_name, device=self.device)
            print(f"模型加载耗时: {time.time() - start_time:.2f}秒")
        return self.model
    
    def transcribe(self, audio_file, language="zh"):
        """
        转录音频文件
        
        Args:
            audio_file (str): 音频文件路径
            language (str): 语言代码，默认为中文(zh)
            
        Returns:
            str: 转录的文本
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"音频文件 '{audio_file}' 不存在")
        
        model = self.load_model()
        
        print(f"正在处理音频文件: {audio_file}")
        start_time = time.time()
        
        result = model.transcribe(
            audio_file,
            language=language,
            task="transcribe",
            fp16=torch.cuda.is_available(),
            initial_prompt="以下是简体中文："
        )
        
        print(f"转录耗时: {time.time() - start_time:.2f}秒")
        print(f"转录完成，文本长度: {len(result['text'])}字符")
        
        if "duration" in result:
            print(f"音频时长: {result['duration']:.2f}秒")
            print(f"平均语速: {len(result['text'])/result['duration']:.2f}字/秒")
        
        return result["text"]
    
    @staticmethod
    def get_model_options():
        """获取可用的模型选项"""
        return {
            '1': 'tiny',
            '2': 'base',
            '3': 'small',
            '4': 'medium',
            '5': 'large'
        }
    
    @staticmethod
    def print_model_info():
        """打印模型信息"""
        print("\n请选择Whisper模型大小:")
        print("1. tiny - 最小模型，速度最快，准确度较低")
        print("2. base - 小型模型，平衡速度和准确度")
        print("3. small - 中型模型，默认选项")
        print("4. medium - 大型模型，准确度较高")
        print("5. large - 最大模型，准确度最高，速度最慢")