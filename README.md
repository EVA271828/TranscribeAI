# 音频转录与总结工具

这是一个使用Whisper进行语音识别，并使用DeepSeek API进行内容总结的工具。

## 项目结构

```
PythonProject/
├── scripts/                    # 主要脚本文件
│   ├── batch_process.py        # 批处理脚本
│   ├── extract_audio_from_video.py # 音频提取脚本
│   ├── extract_audio_gui.py    # 音频提取GUI
│   ├── main.py                 # 主入口文件
│   ├── run_gui.py              # GUI启动脚本
│   └── whisper_utils.py        # Whisper工具函数
├── src/                        # 源代码目录
│   ├── core/                   # 核心功能模块
│   ├── gui/                    # 图形界面模块
│   ├── utils/                  # 工具模块
│   └── config/                 # 配置模块
├── batch_scripts/              # 批处理脚本
│   ├── extract_audio.bat       # 音频提取批处理
│   ├── 转录.bat               # 转录批处理
│   └── 启动音频提取工具.bat    # 启动音频提取工具
├── build_files/                # 编译相关文件
│   ├── build_exe.py            # 打包脚本
│   └── 音频转录与总结工具.spec   # PyInstaller配置
├── config/                     # 配置文件
│   ├── .gitignore              # Git忽略文件
│   └── requirements.txt        # 依赖包列表
├── docs/                       # 文档文件
│   ├── README.md               # 项目说明
│   ├── README_audio_extraction.md # 音频提取说明
│   └── WHISPER_PROGRESS.md     # Whisper进度说明
├── prompts/                    # 提示词模板目录
├── output/                     # 输出目录
├── dist/                       # 打包输出目录
└── .venv/                      # 虚拟环境
```

## 功能特点

1. **模块化结构**: 代码按功能分类到不同文件夹中，便于维护
2. **分离输出**: 转录文本保存为txt文件，总结内容保存为md文件
3. **多模型支持**: 支持Whisper的多种模型(tiny, base, small, medium, large)
4. **多种模板**: 提供多种提示词模板，适应不同场景
5. **配置管理**: 支持保存API密钥和默认设置
6. **图形界面**: 提供友好的GUI界面，方便用户操作
7. **批处理功能**: 支持批量处理多个音频文件
8. **音频提取**: 支持从视频文件中提取音频

## 使用方法

### 图形界面模式（推荐）

```bash
# 启动GUI界面
python scripts/run_gui.py
```

### 命令行模式

```bash
# 基本使用
python scripts/main.py

# 批量处理
python scripts/batch_process.py --source_folder 音频文件夹路径 --output 输出文件夹路径

# 音频提取
python scripts/extract_audio_from_video.py 源文件夹路径 目标文件夹路径
```

## 依赖安装

```bash
pip install -r config/requirements.txt
```

## 注意事项

- 使用前请确保已安装所有依赖包
- 音频提取功能需要安装FFmpeg
- 批处理功能需要配置API密钥
- 详细的文档请参考docs文件夹中的相关文档