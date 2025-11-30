# 提示词模板说明

本目录包含各种用于AI文本处理的提示词模板，这些模板可以与DeepSeek API结合使用，以生成高质量的文本分析结果。

## 模板列表

### 1. audio_content_analysis.txt
**用途**：音频内容深度分析与大纲生成
**适用场景**：对讲座、演讲、播客等音频内容的转录文本进行结构化分析
**变量**：
- `{audio_title}`：音频标题
- `{content}`：音频转录内容

### 2. text_summary.txt
**用途**：通用文本摘要生成
**适用场景**：对文章、报告、文档等文本内容进行简洁总结
**变量**：
- `{title}`：文本标题
- `{content}`：文本内容

### 3. meeting_analysis.txt
**用途**：会议记录分析
**适用场景**：对会议记录进行结构化分析，提取讨论要点和行动项
**变量**：
- `{meeting_title}`：会议主题
- `{meeting_time}`：会议时间
- `{attendees}`：参会人员
- `{content}`：会议内容

### 4. course_analysis.txt
**用途**：课程内容分析
**适用场景**：对课程、讲座、培训等教学内容进行结构化分析
**变量**：
- `{course_title}`：课程标题
- `{instructor}`：讲师
- `{duration}`：课程时长
- `{content}`：课程内容

## 使用方法

1. 选择适合的模板文件
2. 读取模板内容
3. 使用Python的`format()`方法或字符串替换，将变量替换为实际内容
4. 将处理后的提示词发送给DeepSeek API

## 示例代码

```python
# 读取模板
with open('prompts/audio_content_analysis.txt', 'r', encoding='utf-8') as f:
    template = f.read()

# 替换变量
prompt = template.format(
    audio_title="AI时代下的能力提升",
    content="这里是音频转录的文本内容..."
)

# 发送给API
response = deepseek_api.send(prompt)
```

## 添加新模板

如果需要添加新的提示词模板，请按照以下步骤：

1. 在此目录下创建新的`.txt`文件
2. 使用`{变量名}`格式定义可替换的变量
3. 在本文件中添加模板说明
4. 更新相关的代码以支持新模板

## 注意事项

1. 模板文件使用UTF-8编码
2. 变量名使用英文，并用花括号包围
3. 保持模板结构清晰，便于AI理解和生成高质量结果
4. 定期检查和更新模板，以适应不同的应用场景