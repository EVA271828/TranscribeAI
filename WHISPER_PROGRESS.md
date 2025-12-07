# Whisper转录进度功能说明

## 概述

我们已经为Whisper转录器添加了进度显示功能，现在用户可以在转录过程中查看实时进度，而不是只能等待转录完成。

## 功能特点

1. **实时进度显示**：转录过程中显示当前进度百分比
2. **进度条可视化**：提供直观的进度条显示
3. **灵活集成**：可以轻松集成到GUI和命令行应用中
4. **向后兼容**：不影响现有代码的使用方式

## 使用方法

### 1. 基本用法（带进度回调）

```python
from src.core.whisper_transcriber import WhisperTranscriber

# 定义进度回调函数
def progress_callback(progress):
    print(f"转录进度: {progress:.1f}%")

# 初始化转录器
transcriber = WhisperTranscriber(model_name="base")

# 使用进度回调进行转录
transcription = transcriber.transcribe(
    "audio_file.mp3", 
    language="zh", 
    progress_callback=progress_callback
)
```

### 2. GUI应用中的使用

```python
def progress_callback(progress):
    # 更新GUI中的进度条或状态栏
    status_var.set(f"正在转录音频... {progress:.1f}%")
    progress_bar["value"] = progress

# 在转录线程中调用
transcription = transcriber.transcribe(
    audio_file, 
    progress_callback=progress_callback
)
```

### 3. 命令行应用中的使用

```python
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
transcription = transcriber.transcribe(
    audio_file, 
    progress_callback=progress_callback
)
```

## 参数说明

`transcribe`方法新增了两个可选参数：

- `verbose` (bool, 默认为True): 是否显示Whisper的详细输出信息
- `progress_callback` (callable, 可选): 进度回调函数，接收当前进度百分比作为参数

## 实现原理

1. **音频时长获取**：使用librosa库获取音频文件的实际时长
2. **进度计算**：基于Whisper的verbose输出中的时间戳信息计算进度
3. **回调机制**：通过临时替换Python的print函数，捕获Whisper的输出并提取进度信息

## 注意事项

1. **进度估算**：进度是基于音频时间戳计算的，不是基于处理时间，因此可能不是完全线性的
2. **最大进度**：为了避免进度达到100%但转录仍在进行，我们将最大进度限制在95%，转录完成后再设置为100%
3. **音频时长获取**：如果无法获取音频时长，将使用默认估计（假设音频不超过1小时）
4. **性能影响**：进度回调功能对转录性能的影响很小

## 示例文件

项目中提供了以下示例文件：

1. `whisper_progress_example.py` - 基本使用示例
2. `test_whisper_progress.py` - 功能测试脚本
3. 更新后的GUI和命令行应用已集成进度显示功能

## 测试

运行测试脚本验证功能：

```bash
python test_whisper_progress.py
```

运行示例脚本查看效果：

```bash
python whisper_progress_example.py
```

## 更新日志

- 添加了`progress_callback`参数到`transcribe`方法
- 使用librosa库获取音频时长
- 实现了进度计算和回调机制
- 更新了GUI和命令行应用以支持进度显示
- 添加了示例和测试脚本