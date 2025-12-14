import whisper
import torch
import time
import os
import librosa

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
        self._stop_flag = False
        print(f"设备设置为使用 {self.device}")
    
    def stop(self):
        """设置停止标志，用于中断长时间运行的转录"""
        self._stop_flag = True
        print("收到停止信号，正在中断转录...")
    
    def reset_stop_flag(self):
        """重置停止标志"""
        self._stop_flag = False
    
    def load_model(self, status_callback=None):
        """加载Whisper模型"""
        if self.model is None:
            print(f"正在加载模型: {self.model_name}")
            if status_callback:
                status_callback(f"正在加载Whisper模型({self.model_name})...")
            start_time = time.time()
            self.model = whisper.load_model(self.model_name, device=self.device)
            print(f"模型加载耗时: {time.time() - start_time:.2f}秒")
            if status_callback:
                status_callback(f"模型加载完成，耗时{time.time() - start_time:.2f}秒")
        return self.model
    
    def transcribe(self, audio_file, language="zh", verbose=True, progress_callback=None, status_callback=None):
        """
        转录音频文件
        
        Args:
            audio_file (str): 音频文件路径
            language (str): 语言代码，默认为中文(zh)
            verbose (bool): 是否显示详细进度信息，默认为True
            progress_callback (callable): 进度回调函数，接收当前进度百分比作为参数
            status_callback (callable): 状态回调函数，接收状态文本作为参数
            
        Returns:
            str: 转录的文本
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"音频文件 '{audio_file}' 不存在")
        
        model = self.load_model(status_callback)
        
        print(f"正在处理音频文件: {audio_file}")
        if status_callback:
            status_callback(f"正在处理音频文件: {os.path.basename(audio_file)}")
        start_time = time.time()
        
        # 如果提供了进度回调函数，则使用自定义的verbose函数
        if progress_callback is not None and callable(progress_callback):
            # 获取音频时长，使用更健壮的方法
            try:
                # 尝试使用ffmpeg获取音频时长，避免librosa的兼容性问题
                import subprocess
                cmd = [
                    'ffprobe', '-v', 'error', '-show_entries', 
                    'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', 
                    audio_file
                ]
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
                if result.returncode == 0 and result.stdout.strip():
                    audio_duration = float(result.stdout.strip())
                    print(f"音频时长: {audio_duration:.2f}秒")
                else:
                    # 如果ffmpeg失败，尝试使用librosa
                    audio_duration = librosa.get_duration(path=audio_file)
                    print(f"音频时长: {audio_duration:.2f}秒")
            except Exception as e:
                print(f"无法获取音频时长: {e}")
                audio_duration = None
            
            # 保存原始的print函数
            original_print = print
            
            def custom_print(*args, **kwargs):
                # 调用原始print函数以保持控制台输出
                original_print(*args, **kwargs)
                
                # 尝试从输出中提取进度信息
                if len(args) > 0 and isinstance(args[0], str):
                    text = args[0]
                    # Whisper的verbose输出格式通常是 "[00:00.000 --> 00:10.000] 文本内容"
                    if "-->" in text and "[" in text and "]" in text:
                        try:
                            # 提取时间戳
                            time_part = text.split("]")[0].split("[")[1]
                            end_time = time_part.split(" --> ")[1]
                            # 将时间戳转换为秒
                            minutes, seconds = end_time.split(":")
                            total_seconds = int(minutes) * 60 + float(seconds)
                            
                            # 计算进度百分比
                            if audio_duration is not None:
                                progress = min(95, int(total_seconds * 100 / audio_duration))
                            else:
                                # 如果无法获取音频时长，使用默认估计
                                progress = min(95, int(total_seconds * 100 / 3600))  # 假设最大1小时
                            
                            progress_callback(progress)
                        except:
                            pass
            
            # 临时替换print函数
            import builtins
            builtins.print = custom_print
            
            try:
                # 在转录前检查停止标志
                if self._stop_flag:
                    print("转录被用户中断")
                    return ""
                    
                result = model.transcribe(
                    audio_file,
                    language=language,
                    task="transcribe",
                    fp16=torch.cuda.is_available(),
                    initial_prompt="以下是简体中文：",
                    verbose=verbose
                )
                
                # 转录完成后检查是否被中断
                if self._stop_flag:
                    print("转录被用户中断")
                    return ""
                    
            finally:
                # 恢复原始print函数
                builtins.print = original_print
        else:
            # 没有提供进度回调，使用标准方式
            # 在转录前检查停止标志
            if self._stop_flag:
                print("转录被用户中断")
                return ""
                
            result = model.transcribe(
                audio_file,
                language=language,
                task="transcribe",
                fp16=torch.cuda.is_available(),
                initial_prompt="以下是简体中文：",
                verbose=verbose
            )
            
            # 转录完成后检查是否被中断
            if self._stop_flag:
                print("转录被用户中断")
                return ""
        
        print(f"转录耗时: {time.time() - start_time:.2f}秒")
        print(f"转录完成，文本长度: {len(result['text'])}字符")
        
        # 如果提供了进度回调，通知完成
        if progress_callback is not None and callable(progress_callback):
            progress_callback(100)
        
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