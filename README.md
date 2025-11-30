# 音频转录与总结工具

这是一个使用Whisper进行语音识别，并使用DeepSeek API进行内容总结的工具。

## 项目结构

```
PythonProject/
├── main.py                     # 主入口文件
├── run_gui.py                  # GUI启动脚本
├── src/                        # 源代码目录
│   ├── core/                   # 核心功能模块
│   │   ├── audio_summarizer.py # 主程序逻辑
│   │   ├── whisper_transcriber.py # Whisper语音识别
│   │   └── deepseek_summarizer.py # DeepSeek API总结
│   ├── gui/                    # 图形界面模块
│   │   └── main_gui.py         # GUI主程序
│   ├── utils/                  # 工具模块
│   │   └── file_utils.py       # 文件操作工具
│   └── config/                 # 配置模块
│       ├── config_manager.py   # 配置管理器
│       ├── config.ini          # 配置文件
│       └── config.example.ini  # 配置文件示例
├── prompts/                    # 提示词模板目录
│   ├── audio_content_analysis.txt
│   ├── course_analysis.txt
│   ├── meeting_analysis.txt
│   └── text_summary.txt
├── output/                     # 输出目录
│   ├── transcripts/            # 转录文本(txt格式)
│   └── summaries/              # 总结内容(md格式)
└── requirements.txt            # 依赖包列表
```

## 功能特点

1. **模块化结构**: 代码按功能分类到不同文件夹中，便于维护
2. **分离输出**: 转录文本保存为txt文件，总结内容保存为md文件
3. **多模型支持**: 支持Whisper的多种模型(tiny, base, small, medium, large)
4. **多种模板**: 提供多种提示词模板，适应不同场景
5. **配置管理**: 支持保存API密钥和默认设置
6. **图形界面**: 提供友好的GUI界面，方便用户操作

## 使用方法

### 图形界面模式（推荐）

```bash
# 方法1：直接运行GUI脚本
python run_gui.py

# 方法2：通过主程序启动GUI
python main.py --gui
```

图形界面功能：
- 可视化选择音频文件
- 直观选择Whisper模型和总结模板
- 实时显示转录和总结进度
- 内置配置管理界面

### 命令行模式

```bash
# 基本使用
python main.py

# 指定模型
python main.py --model tiny

# 指定音频文件
python main.py --audio your_audio.mp3

# 指定API密钥
python main.py --api_key YOUR_API_KEY

# 指定模板
python main.py --template text_summary

# 进入配置模式
python main.py --config
```

## 输出文件

- **转录文本**: 保存在 `output/transcripts/` 目录下，文件名格式为 `{音频名称}_转录_{时间戳}.txt`
- **总结内容**: 保存在 `output/summaries/` 目录下，文件名格式为 `{音频名称}_总结_{时间戳}.md`

## 配置

首次运行时，建议使用 `--config` 参数进入配置模式，设置API密钥和默认选项。

## 依赖安装

```bash
pip install -r requirements.txt
```

### 默认设置
- `default_model`: 默认使用的Whisper模型（tiny/base/small/medium/large）
- `default_template`: 默认使用的提示词模板

### 配置文件格式
```ini
[api]
api_key = YOUR_DEEPSEEK_API_KEY_HERE

[settings]
default_model = small
default_template = audio_content_analysis
```

### 安全注意事项
1. 请勿将包含真实API密钥的`config.ini`文件提交到公共代码仓库
2. 建议将`config.ini`添加到`.gitignore`文件中
3. API密钥在配置文件中以明文存储，请确保文件安全

### FileUtils 类

负责文件操作，主要方法：
- `save_results(transcription, summary, audio_file)`: 保存转录和总结结果
- `check_file_exists(file_path)`: 检查文件是否存在
- `get_audio_title(audio_file)`: 从音频文件路径获取标题

## 提示词模板系统

### 模板类型

1. **audio_content_analysis**：音频内容深度分析与大纲生成
   - 适用于：讲座、演讲、播客等音频内容
   - 输出：综合摘要、详尽内容大纲、结论与行动项

2. **text_summary**：通用文本摘要生成
   - 适用于：文章、报告、文档等文本内容
   - 输出：文本摘要、关键要点、结论

3. **meeting_analysis**：会议记录分析
   - 适用于：会议记录、讨论内容
   - 输出：会议概述、讨论要点、决策与行动项、后续跟进

4. **course_analysis**：课程内容分析
   - 适用于：课程、讲座、培训等教学内容
   - 输出：课程概述、知识点梳理、重点与难点、实践应用、学习建议

### 自定义模板

用户可以创建自定义的提示词模板：

1. 在`prompts`目录下创建新的`.txt`文件
2. 使用`{变量名}`格式定义可替换的变量
3. 使用`--template`参数指定新模板

#### 示例：创建自定义模板

1. 创建文件 `prompts/custom_analysis.txt`
2. 编写模板内容，使用变量如 `{title}`、`{content}` 等
3. 使用命令：`python audio_summarizer.py --template custom_analysis`

### 模板变量

不同模板支持的变量可能不同，常见的变量包括：
- `{audio_title}`：音频标题
- `{content}`：文本内容
- `{title}`：通用标题
- `{meeting_title}`：会议主题
- `{meeting_time}`：会议时间
- `{attendees}`：参会人员
- `{course_title}`：课程标题
- `{instructor}`：讲师
- `{duration}`：时长