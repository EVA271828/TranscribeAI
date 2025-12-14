# 音频转录与总结工具

一个基于Whisper和DeepSeek的音频转录与内容总结工具，支持单个文件处理和批量处理，提供图形化界面和命令行界面。

## 功能特点

- 🎵 **音频转录**：使用OpenAI Whisper模型将音频转换为文本
- 📝 **智能总结**：使用DeepSeek API对转录内容进行智能总结
- 🖥️ **多种界面**：提供图形化界面和命令行界面
- 📁 **批量处理**：支持批量处理整个文件夹中的音频文件
- 🔄 **保持结构**：批量处理时保持源文件夹结构
- 🎬 **视频音频提取**：支持从视频文件中提取音频
- ⚙️ **多模型支持**：支持多种Whisper模型（tiny, base, small, medium, large）
- 📋 **多种模板**：提供多种内容总结模板
- ⚙️ **配置管理**：支持保存配置信息，包括API密钥和默认设置

## 安装说明

### 环境要求

- Python 3.8+
- CUDA（可选，用于GPU加速）

### 安装步骤

1. 克隆或下载项目到本地
2. 创建虚拟环境（推荐）：
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

### 图形化界面（推荐）

直接运行主程序：
```bash
python main.py
```

### 命令行界面

#### 单个文件处理
```bash
python main.py --cli
```

#### 批量处理
```bash
python main.py --batch --source_folder 源文件夹路径 --output 输出文件夹路径
```

#### 配置模式
```bash
python main.py --config
```

### 高级用法

#### 指定模型
```bash
python main.py --cli --model tiny  # 可选: tiny, base, small, medium, large
```

#### 指定输出文件夹
```bash
python main.py --cli --output 自定义输出路径
```

#### 指定总结模板
```bash
python main.py --cli --template text_summary  # 可选: audio_content_analysis, course_analysis, meeting_analysis, text_summary
```

#### 指定API密钥
```bash
python main.py --cli --api_key YOUR_API_KEY
```

## 提示词模板

项目提供多种内容总结模板，位于`prompts`目录：

- `audio_content_analysis.txt`：音频内容深度分析（默认）
- `course_analysis.txt`：课程内容分析
- `meeting_analysis.txt`：会议内容分析
- `text_summary.txt`：文本摘要

您可以根据需要创建自定义模板。

## 视频音频提取

工具支持从视频文件中提取音频：

```bash
python extract_audio/extract_audio_from_video.py 源视频文件夹路径 目标音频文件夹路径
```

支持的视频格式：mp4, avi, mov, mkv, wmv, flv, webm, m4v, 3gp

## 配置说明

首次使用时，建议运行配置模式设置默认值：

```bash
python main.py --config
```

可配置项包括：
- DeepSeek API密钥
- 默认Whisper模型
- 默认总结模板
- 默认输出文件夹

## 项目结构

```
PythonProject/
├── main.py                    # 主程序入口
├── requirements.txt           # 依赖包列表
├── src/                       # 源代码目录
│   ├── config/               # 配置管理
│   │   ├── config.ini        # 配置文件
│   │   └── config_manager.py # 配置管理器
│   ├── core/                 # 核心功能
│   │   ├── audio_summarizer.py     # 音频总结主程序
│   │   ├── batch_process.py        # 批量处理
│   │   ├── deepseek_summarizer.py  # DeepSeek总结器
│   │   └── whisper_transcriber.py  # Whisper转录器
│   ├── gui/                  # 图形界面
│   │   └── main_gui.py       # 主GUI程序
│   └── utils/                # 工具函数
│       ├── file_utils.py     # 文件操作工具
│       └── whisper_utils.py  # Whisper相关工具
├── prompts/                  # 提示词模板
│   ├── audio_content_analysis.txt
│   ├── course_analysis.txt
│   ├── meeting_analysis.txt
│   └── text_summary.txt
└── extract_audio/            # 音频提取工具
    ├── extract_audio_from_video.py
    └── extract_audio_gui.py
```

## 常见问题

### 1. 转录速度慢

- 尝试使用更小的模型（如tiny或base）
- 确保安装了CUDA并使用GPU加速

### 2. API调用失败

- 检查DeepSeek API密钥是否正确
- 确认网络连接正常
- 检查API配额是否用完

### 3. 内存不足

- 使用更小的Whisper模型
- 减少批量处理的并发线程数

## 技术栈

- **音频转录**：OpenAI Whisper
- **内容总结**：DeepSeek API
- **GUI框架**：Tkinter
- **音频处理**：librosa, soundfile
- **视频处理**：FFmpeg

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交问题和改进建议！

## 更新日志

### v1.0.0
- 初始版本发布
- 支持音频转录与总结
- 提供图形化界面和命令行界面
- 支持批量处理和视频音频提取