# Scripts 文件夹文档

## 概述

`scripts` 文件夹包含了音频转录与总结工具的各种脚本文件，包括主程序入口、批处理工具、音频提取工具等。这些脚本提供了命令行界面和图形用户界面，方便用户使用不同的功能。

## 脚本文件列表

### 1. main.py

**功能**: 音频转录与总结工具的主入口文件，提供命令行界面和图形界面两种启动方式。

**用法**:
```bash
# 启动命令行界面
python main.py

# 启动图形化界面
python main.py --gui

# 指定输出文件夹路径
python main.py --output /path/to/output
```

**参数**:
- `--gui`: 启动图形化界面
- `--output`: 指定输出文件夹路径

### 2. run_gui.py

**功能**: 启动图形化界面的快捷脚本，直接调用主GUI程序。

**用法**:
```bash
python run_gui.py
```

### 3. whisper_utils.py

**功能**: Whisper语音识别工具，提供命令行界面进行音频转录。

**用法**:
```bash
# 直接运行（交互式选择模型）
python whisper_utils.py

# 指定模型
python whisper_utils.py --model tiny

# 指定模型和音频文件
python whisper_utils.py --model base --audio your_audio.mp3
```

**参数**:
- `--model`: 选择Whisper模型大小 (tiny, base, small, medium, large)
- `--audio`: 音频文件路径

**支持的模型**:
- tiny: 最小模型，速度最快，准确度较低
- base: 小型模型，平衡速度和准确度
- small: 中型模型，默认选项
- medium: 大型模型，准确度较高
- large: 最大模型，准确度最高，速度最慢

### 4. batch_process.py

**功能**: 批处理脚本，处理整个文件夹中的音频文件，并保持源文件夹结构。支持多线程并发处理。

**用法**:
```bash
python batch_process.py --source_folder /path/to/source --output /path/to/output [其他参数]
```

**参数**:
- `--source_folder`: 源文件夹路径（包含音频文件）[必需]
- `--output`: 输出文件夹路径 [必需]
- `--model`: 选择Whisper模型大小 (tiny, base, small, medium, large)
- `--api_key`: DeepSeek API密钥
- `--template`: 使用的提示词模板名称（不含扩展名），默认为audio_content_analysis
- `--prompts_dir`: 提示词模板目录，默认为prompts
- `--threads`: 并发处理的线程数，默认为1

**功能特点**:
- 递归扫描源文件夹中的所有音频文件
- 保持源文件夹结构在输出中
- 支持多线程并发处理
- 实时显示处理进度
- 自动保存转录和总结结果

### 5. extract_audio_from_video.py

**功能**: 使用FFmpeg从视频文件中提取音频，并保持源文件夹结构。

**用法**:
```bash
python extract_audio_from_video.py 源文件夹路径 目标文件夹路径 [--ffmpeg-path FFmpeg路径]
```

**参数**:
- `source_dir`: 源文件夹路径 [必需]
- `target_dir`: 目标文件夹路径 [必需]
- `--ffmpeg-path`: FFmpeg可执行文件路径，默认为 `D:\software\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe`

**支持的视频格式**:
- .mp4, .avi, .mov, .mkv, .wmv, .flv, .webm, .m4v, .3gp

**输出格式**:
- WAV格式 (PCM 16位, 16kHz采样率, 单声道)

### 6. extract_audio_gui.py

**功能**: 视频音频提取工具的图形界面版本，提供友好的用户界面进行音频提取操作。

**用法**:
```bash
python extract_audio_gui.py
```

**功能特点**:
- 图形化界面操作
- 可选择源文件夹和目标文件夹
- 可自定义FFmpeg路径
- 实时显示处理进度和日志
- 支持中断处理

### 7. 批处理脚本

#### extract_audio.bat

**功能**: Windows批处理脚本，使用FFmpeg从视频文件中提取音频，并保持源文件夹结构。

**用法**:
```bash
extract_audio.bat 源文件夹路径 目标文件夹路径
```

**示例**:
```bash
extract_audio.bat "D:\Videos" "D:\Audio"
```

**特点**:
- 纯批处理实现，无需Python环境
- 自动创建目标目录结构
- 支持多种视频格式
- 跳过已存在的文件

#### 启动音频提取工具.bat

**功能**: 启动视频音频提取工具GUI的快捷批处理脚本。

**用法**:
双击运行或在命令行中执行：
```bash
启动音频提取工具.bat
```

#### 转录.bat

**功能**: 启动音频转录与总结工具的快捷批处理脚本。

**用法**:
双击运行或在命令行中执行：
```bash
转录.bat
```

## 使用流程

### 完整工作流程

1. **从视频中提取音频** (如果需要):
   - 使用 `extract_audio_gui.py` (图形界面) 或 `extract_audio_from_video.py` (命令行)
   - 或使用 `extract_audio.bat` (批处理脚本)

2. **音频转录与总结**:
   - 使用 `main.py --gui` (图形界面)
   - 或使用 `main.py` (命令行界面)
   - 或使用 `转录.bat` (快捷方式)

3. **批量处理**:
   - 使用 `batch_process.py` 批量处理多个音频文件

### 仅音频转录

1. 使用 `whisper_utils.py` 进行简单的音频转录
2. 使用 `main.py` 进行音频转录和总结

## 依赖项

- Python 3.7+
- FFmpeg (用于视频音频提取)
- 依赖的Python包 (详见 requirements.txt):
  - whisper
  - torch
  - tkinter (用于GUI)
  - 其他相关依赖

## 注意事项

1. 确保FFmpeg已正确安装并配置路径，特别是在使用音频提取功能时
2. 使用GPU加速可以显著提高转录速度
3. 批量处理时注意系统资源使用情况，适当调整线程数
4. API密钥应妥善保管，不要在代码中硬编码
5. 大文件处理可能需要较长时间，请耐心等待

## 故障排除

1. **FFmpeg相关错误**:
   - 检查FFmpeg路径是否正确
   - 确认FFmpeg可执行文件是否存在

2. **模型加载错误**:
   - 检查网络连接
   - 尝试使用较小的模型
   - 确认有足够的磁盘空间

3. **GUI启动失败**:
   - 检查tkinter是否正确安装
   - 确认Python环境配置正确

4. **批处理权限问题**:
   - 以管理员身份运行
   - 检查文件夹权限设置