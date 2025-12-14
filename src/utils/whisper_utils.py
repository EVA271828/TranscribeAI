import whisper
import torch
import os
import time
import argparse

# 检查是否有GPU，如果有则使用GPU加速
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device set to use {device}")

print("\n=== Whisper语音识别工具 ===")
print("使用方法:")
print("1. 直接运行: python 'whisper_utils.py'")
print("2. 指定模型: python 'whisper_utils.py' --model tiny")
print("3. 指定音频文件: python 'whisper_utils.py' --model base --audio your_audio.mp3")
print("========================\n")

# 解析命令行参数
parser = argparse.ArgumentParser(description='Whisper语音识别工具')
parser.add_argument('--model', type=str, 
                    choices=['tiny', 'base', 'small', 'medium', 'large'],
                    help='选择Whisper模型大小')
parser.add_argument('--audio', type=str, 
                    help='音频文件路径')
args = parser.parse_args()

# 如果没有提供模型参数，则交互式选择
if args.model is None:
    print("\n请选择Whisper模型大小:")
    print("1. tiny - 最小模型，速度最快，准确度较低")
    print("2. base - 小型模型，平衡速度和准确度")
    print("3. small - 中型模型，默认选项")
    print("4. medium - 大型模型，准确度较高")
    print("5. large - 最大模型，准确度最高，速度最慢")
    
    model_options = {
        '1': 'tiny',
        '2': 'base',
        '3': 'small',
        '4': 'medium',
        '5': 'large'
    }
    
    while True:
        choice = input("请输入选项(1-5，默认为3): ").strip()
        if not choice:
            choice = '3'
        if choice in model_options:
            model_path = model_options[choice]
            break
        print("无效选项，请重新输入")
else:
    model_path = args.model

# 如果没有提供音频文件参数，则使用默认值
if args.audio is None:
    audio_file = "F:\project\my-project\PythonProject\AI可以取代我，那我的意义是？_哔哩哔哩_bilibili.mp3"
else:
    audio_file = args.audio

# 加载Whisper模型
print(f"正在加载模型: {model_path}")
start_time = time.time()
model = whisper.load_model(model_path, device=device)
print(f"模型加载耗时: {time.time() - start_time:.2f}秒")

# 检查文件是否存在
if os.path.exists(audio_file):
    print(f"Processing audio file: {audio_file}")
    # 执行转录任务，指定中文识别
    start_time = time.time()
    result = model.transcribe(
        audio_file,
        language="zh",  # 指定中文识别
        task="transcribe",  # 明确指定转录任务
        fp16=torch.cuda.is_available(),  # 如果有GPU则使用半精度
        initial_prompt="以下是简体中文："  # 提示模型使用简体中文
    )
    print(f"转录耗时: {time.time() - start_time:.2f}秒")
    
    print("\nTranscription result:")
    print(result["text"])
    
    # 输出关键信息
    print(f"转录完成，文本长度: {len(result['text'])}字符")
    if "duration" in result:
        print(f"音频时长: {result['duration']:.2f}秒")
        print(f"平均语速: {len(result['text'])/result['duration']:.2f}字/秒")
else:
    print(f"错误：音频文件 '{audio_file}' 不存在。请提供有效的音频文件路径。")
    print("提示：你可以将音频文件放在与脚本相同的目录下，或提供完整的文件路径。")