import argparse
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.whisper_transcriber import WhisperTranscriber
from src.core.deepseek_summarizer import DeepSeekSummarizer
from src.utils.file_utils import FileUtils
from src.config.config_manager import ConfigManager

def main(output_folder=None):
    """主程序"""
    # 初始化配置管理器
    config = ConfigManager()
    
    print("\n=== Whisper语音识别与DeepSeek总结工具 ===")
    print("使用方法:")
    print("1. 直接运行: python 'audio_summarizer.py'")
    print("2. 指定模型: python 'audio_summarizer.py' --model tiny")
    print("3. 指定音频文件: python 'audio_summarizer.py' --model base --audio your_audio.mp3")
    print("4. 指定API密钥: python 'audio_summarizer.py' --api_key YOUR_API_KEY")
    print("5. 指定模板: python 'audio_summarizer.py' --template text_summary")
    print("6. 指定模板目录: python 'audio_summarizer.py' --prompts_dir custom_prompts")
    print("7. 指定输出文件夹: python 'audio_summarizer.py' --output output_folder")
    print("8. 指定源文件夹(保持文件夹结构): python 'audio_summarizer.py' --source_folder source_folder --output output_folder")
    print("9. 设置配置: python 'audio_summarizer.py' --config")
    print("=========================================\n")

    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Whisper语音识别与DeepSeek总结工具')
    parser.add_argument('--model', type=str, 
                        choices=['tiny', 'base', 'small', 'medium', 'large'],
                        help='选择Whisper模型大小')
    parser.add_argument('--audio', type=str, 
                        help='音频文件路径')
    parser.add_argument('--source_folder', type=str,
                        help='源文件夹路径（用于保持文件夹结构）')
    parser.add_argument('--api_key', type=str,
                        help='DeepSeek API密钥')
    parser.add_argument('--template', type=str, default='audio_content_analysis',
                        help='使用的提示词模板名称（不含扩展名），默认为audio_content_analysis')
    parser.add_argument('--prompts_dir', type=str, default='prompts',
                        help='提示词模板目录，默认为prompts')
    parser.add_argument('--output', type=str,
                        help='指定输出文件夹路径')
    parser.add_argument('--config', action='store_true',
                        help='进入配置模式，设置API密钥和默认选项')
    args = parser.parse_args()
    
    # 如果是配置模式，则进入配置界面
    if args.config:
        enter_config_mode(config)
        return

    # 如果没有提供模型参数，则使用配置中的默认值或交互式选择
    if args.model is None:
        # 尝试从配置中获取默认模型
        default_model = config.get_default_model()
        if default_model:
            model_path = default_model
            print(f"使用配置中的默认模型: {model_path}")
        else:
            # 如果配置中没有默认模型，则交互式选择
            WhisperTranscriber.print_model_info()
            model_options = WhisperTranscriber.get_model_options()
            
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
            # 询问是否保存API密钥到配置文件
            save_key = input("是否将API密钥保存到配置文件以便下次使用？(y/n): ").strip().lower()
            if save_key == 'y' or save_key == 'yes':
                config.set_api_key(api_key)
                print("API密钥已保存到配置文件。")

    # 检查音频文件是否存在
    if not FileUtils.check_file_exists(audio_file):
        print(f"错误：音频文件 '{audio_file}' 不存在。请提供有效的音频文件路径。")
        return

    # 初始化Whisper转录器
    transcriber = WhisperTranscriber(model_path)
    
    # 初始化DeepSeek总结器
    summarizer = DeepSeekSummarizer(api_key, args.prompts_dir)
    
    # 获取音频标题
    audio_title = FileUtils.get_audio_title(audio_file)
    
    # 计算相对路径（如果需要保持源文件夹结构）
    rel_path = None
    if args.source_folder and args.output:
        # 如果提供了源文件夹和输出文件夹，则计算相对路径
        try:
            # 获取音频文件的绝对路径
            abs_audio_file = os.path.abspath(audio_file)
            # 获取源文件夹的绝对路径
            abs_source_folder = os.path.abspath(args.source_folder)
            
            # 如果音频文件在源文件夹内，计算相对路径
            if abs_audio_file.startswith(abs_source_folder):
                rel_path = os.path.relpath(abs_audio_file, abs_source_folder)
        except Exception:
            # 如果计算相对路径失败，则忽略
            rel_path = None
    
    try:
        # 步骤1: 语音识别
        print("\n=== 开始语音识别 ===")
        
        # 定义进度回调函数
        def progress_callback(progress):
            # 创建一个简单的进度条
            bar_length = 50
            filled_length = int(round(bar_length * progress / 100))
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            
            # 使用回车符覆盖当前行，实现进度条更新效果
            print(f'\r进度: |{bar}| {progress:.1f}% ', end='', flush=True)
            
            # 如果完成，打印换行
            if progress >= 100:
                print()
        
        # 使用进度回调进行转录
        transcription = transcriber.transcribe(audio_file, progress_callback=progress_callback)
        
        # 步骤2: 内容总结
        print("\n=== 开始内容总结 ===")
        summary = summarizer.summarize(transcription, audio_title, args.template)
        
        # 步骤3: 保存结果
        print("\n=== 保存结果 ===")
        
        # 确定输出文件夹
        final_output_folder = args.output if args.output else output_folder
        if not final_output_folder:
            # 如果命令行和函数参数都没有提供，则使用配置中的默认值
            final_output_folder = config.get_output_folder()
        
        # 使用相对路径保存结果，以保持源文件夹结构
        transcript_file, summary_file = FileUtils.save_results(
            transcription, summary, audio_file, final_output_folder, rel_path
        )
        
        print("\n处理完成！")
        print(f"转录文本长度: {len(transcription)}字符")
        print(f"总结文本长度: {len(summary)}字符")
        print(f"转录文本已保存到: {transcript_file}")
        print(f"总结内容已保存到: {summary_file}")
        
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")

def enter_config_mode(config):
    """进入配置模式，允许用户设置API密钥和默认选项"""
    print("\n=== 配置模式 ===")
    print("1. 设置API密钥")
    print("2. 设置默认模型")
    print("3. 设置默认模板")
    print("4. 设置默认输出文件夹")
    print("5. 查看当前配置")
    print("6. 退出配置模式")
    
    while True:
        choice = input("\n请选择操作 (1-6): ").strip()
        
        if choice == '1':
            # 设置API密钥
            api_key = input("请输入DeepSeek API密钥: ").strip()
            if api_key:
                config.set_api_key(api_key)
                print("API密钥已保存。")
            else:
                print("API密钥不能为空。")
        
        elif choice == '2':
            # 设置默认模型
            print("\n可用模型:")
            print("1. tiny - 最快，准确度较低")
            print("2. base - 较快，准确度中等")
            print("3. small - 平衡速度与准确度")
            print("4. medium - 较慢，准确度高")
            print("5. large - 最慢，准确度最高")
            
            model_choice = input("请选择默认模型 (1-5): ").strip()
            model_map = {
                '1': 'tiny',
                '2': 'base',
                '3': 'small',
                '4': 'medium',
                '5': 'large'
            }
            
            if model_choice in model_map:
                config.set_default_model(model_map[model_choice])
                print(f"默认模型已设置为: {model_map[model_choice]}")
            else:
                print("无效选择。")
        
        elif choice == '3':
            # 设置默认模板
            print("\n可用模板:")
            print("1. audio_content_analysis - 音频内容深度分析")
            print("2. text_summary - 通用文本摘要")
            print("3. meeting_analysis - 会议记录分析")
            print("4. course_analysis - 课程内容分析")
            
            template_choice = input("请选择默认模板 (1-4): ").strip()
            template_map = {
                '1': 'audio_content_analysis',
                '2': 'text_summary',
                '3': 'meeting_analysis',
                '4': 'course_analysis'
            }
            
            if template_choice in template_map:
                config.set_default_template(template_map[template_choice])
                print(f"默认模板已设置为: {template_map[template_choice]}")
            else:
                print("无效选择。")
        
        elif choice == '4':
            # 设置默认输出文件夹
            current_output = config.get_output_folder()
            print(f"\n当前默认输出文件夹: {current_output}")
            new_output = input("请输入新的默认输出文件夹路径 (留空保持不变): ").strip()
            if new_output:
                config.set_output_folder(new_output)
                print(f"默认输出文件夹已设置为: {new_output}")
        
        elif choice == '5':
            # 查看当前配置
            api_key = config.get_api_key()
            if api_key:
                masked_key = api_key[:10] + "..." + api_key[-4:]
                print(f"API密钥: {masked_key}")
            else:
                print("API密钥: 未设置")
            
            print(f"默认模型: {config.get_default_model()}")
            print(f"默认模板: {config.get_default_template()}")
            print(f"默认输出文件夹: {config.get_output_folder()}")
        
        elif choice == '6':
            # 退出配置模式
            print("退出配置模式。")
            break
        
        else:
            print("无效选择，请重新输入。")

if __name__ == "__main__":
    main()