# 视频音频提取工具

本工具使用FFmpeg从视频文件中提取音频，并保持源文件夹结构，输出为Whisper支持的WAV格式。

## 文件说明

1. **extract_audio_from_video.py** - Python版本的视频音频提取脚本
2. **extract_audio.bat** - 批处理版本的视频音频提取脚本
3. **extract_audio_gui.py** - GUI版本的视频音频提取工具
4. **启动音频提取工具.bat** - GUI版本的快速启动脚本
5. **README_audio_extraction.md** - 本说明文档

## 使用方法

### GUI版本（推荐）

1. **直接运行启动脚本**（最简单）：
   ```cmd
   双击"启动音频提取工具.bat"
   ```

2. **通过Python运行**：
   ```bash
   python extract_audio_gui.py
   ```

GUI版本提供直观的图形界面，包括：
- FFmpeg路径设置
- 源文件夹和目标文件夹选择
- 实时进度显示
- 处理日志查看
- 开始/停止控制

### Python版本

```bash
python extract_audio_from_video.py 源文件夹路径 目标文件夹路径
```

示例：
```bash
python extract_audio_from_video.py "D:\Videos" "D:\Audio"
```

可选参数：
- `--ffmpeg-path`: 指定FFmpeg可执行文件路径（默认为：D:\software\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe）

### 批处理版本

```cmd
extract_audio.bat 源文件夹路径 目标文件夹路径
```

示例：
```cmd
extract_audio.bat "D:\Videos" "D:\Audio"
```

## 功能特点

1. **保持源文件夹结构**：输出文件会保持与源文件相同的目录结构
2. **支持多种视频格式**：MP4、AVI、MOV、MKV、WMV、FLV、WebM、M4V、3GP等
3. **优化音频格式**：
   - 格式：WAV（Whisper支持）
   - 采样率：16kHz（Whisper推荐）
   - 声道：单声道
   - 编码：PCM 16位
4. **智能跳过已存在文件**：如果目标文件已存在，将自动跳过，避免重复处理

## 注意事项

1. 确保FFmpeg已正确安装在指定路径
2. 目标文件夹会自动创建（如果不存在）
3. 如果输出文件已存在，将会跳过处理，不会覆盖
4. 处理大量文件可能需要较长时间，请耐心等待

## 错误处理

如果遇到以下错误：
- "FFmpeg未找到"：请检查FFmpeg路径是否正确
- "源目录不存在"：请确认输入的源文件夹路径是否正确
- 处理失败：可能是视频文件损坏或不支持的格式

## 示例输出

```
找到 5 个视频文件
正在处理: D:\Videos\lecture1.mp4
音频已提取: D:\Audio\lecture1.wav
正在处理: D:\Videos\subfolder\meeting.avi
跳过已存在的文件: D:\Audio\subfolder\meeting.wav
正在处理: D:\Videos\presentation.mkv
音频已提取: D:\Audio\presentation.wav
...

处理完成!
成功: 5 个文件
失败: 0 个文件
```