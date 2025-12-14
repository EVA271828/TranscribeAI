#!/usr/bin/env python3
"""
打包脚本 - 将音频转录与总结工具打包成exe
"""

import os
import sys
import subprocess
import shutil

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller安装失败: {e}")
        return False

def build_exe():
    """构建exe文件"""
    print("开始构建exe文件...")
    
    # 创建dist目录
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # 构建命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=音频转录与总结工具",
        "--windowed",  # 使用GUI模式，不显示控制台窗口
        "--onefile",   # 打包成单个exe文件
        "--icon=NONE",  # 可以指定图标文件
        "--add-data=src;src",  # 包含src目录
        "--add-data=prompts;prompts",  # 包含prompts目录
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.scrolledtext",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=PIL",
        "--hidden-import=whisper",
        "--hidden-import=torch",
        "--hidden-import=transformers",
        "--hidden-import=requests",
        "--hidden-import=yaml",
        "run_gui.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("exe文件构建成功!")
        print(f"输出文件位置: {os.path.abspath('dist/音频转录与总结工具.exe')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"exe文件构建失败: {e}")
        return False

def create_portable_package():
    """创建便携式包，包含必要的配置文件和目录"""
    print("创建便携式包...")
    
    # 创建输出目录
    portable_dir = "dist/音频转录与总结工具_便携版"
    if os.path.exists(portable_dir):
        shutil.rmtree(portable_dir)
    os.makedirs(portable_dir)
    
    # 复制exe文件
    shutil.copy("dist/音频转录与总结工具.exe", portable_dir)
    
    # 复制必要的目录
    if os.path.exists("prompts"):
        shutil.copytree("prompts", f"{portable_dir}/prompts")
    
    # 创建输出目录
    os.makedirs(f"{portable_dir}/output/transcripts", exist_ok=True)
    os.makedirs(f"{portable_dir}/output/summaries", exist_ok=True)
    
    # 创建配置文件示例
    if os.path.exists("src/config/config.example.ini"):
        os.makedirs(f"{portable_dir}/config", exist_ok=True)
        shutil.copy("src/config/config.example.ini", f"{portable_dir}/config/config.ini")
    
    # 创建使用说明
    readme_content = """# 音频转录与总结工具 - 便携版

## 使用方法

1. 双击运行"音频转录与总结工具.exe"
2. 在界面中点击"浏览..."选择要转录的音频文件
3. 输入DeepSeek API密钥
4. 选择Whisper模型和总结模板
5. 点击"开始转录"按钮
6. 等待转录和总结完成
7. 点击"保存结果"保存转录和总结内容

## 注意事项

1. 首次使用需要输入DeepSeek API密钥
2. 转录大文件可能需要较长时间，请耐心等待
3. 转录结果将保存在output目录下

## 目录说明

- prompts/: 提示词模板目录
- output/: 输出目录，包含转录文本和总结内容
- config/: 配置文件目录
"""
    
    with open(f"{portable_dir}/使用说明.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"便携式包创建成功: {os.path.abspath(portable_dir)}")

def main():
    """主函数"""
    print("=== 音频转录与总结工具 - 打包脚本 ===")
    
    # 检查是否安装了PyInstaller
    try:
        subprocess.check_call([sys.executable, "-m", "PyInstaller", "--version"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("检测到PyInstaller已安装")
    except subprocess.CalledProcessError:
        print("未检测到PyInstaller，正在安装...")
        if not install_pyinstaller():
            return
    
    # 构建exe文件
    if build_exe():
        # 创建便携式包
        create_portable_package()
        print("\n打包完成！")
        print(f"单文件exe: {os.path.abspath('dist/音频转录与总结工具.exe')}")
        print(f"便携版目录: {os.path.abspath('dist/音频转录与总结工具_便携版')}")
    else:
        print("打包失败！")

if __name__ == "__main__":
    main()