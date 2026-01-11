## CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **Audio Transcription and Summarization Tool** (音频转录与总结工具) that combines OpenAI's Whisper for speech-to-text with DeepSeek API for AI-powered content summarization. The project is primarily documented in Chinese.

## Development Commands

### Running the Application

```bash
# GUI (default mode)
python main.py

# CLI mode (single file)
python main.py --cli

# Batch processing mode
python main.py --batch --source_folder <path> --output <path>
python src/core/batch_process.py --source_folder <path> --output <path> --threads 4

# Configuration mode (set API keys, defaults)
python main.py --config

# Direct core module execution
python src/core/audio_summarizer.py --model small --audio file.mp3
python src/core/batch_process.py --source_folder <path> --output <path> --threads 4
```

### Installing Dependencies

```bash
# Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/Mac

# Install PyTorch first - choose based on hardware:
# CPU-only:
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu

# GPU (CUDA 13.0 example - check nvidia-smi for your version):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130

# Install other dependencies
pip install -r requirements.txt
```

### Audio Extraction from Video

```bash
# CLI
python extract_audio/extract_audio_from_video.py <source_dir> <target_dir> --ffmpeg-path <path_to_ffmpeg>

# GUI (via batch file)
extract_audio\启动音频提取工具.bat
```

## Architecture

### Entry Points

- **`main.py`** - Main launcher that routes to GUI, CLI, or batch mode based on command-line arguments
- **`src/gui/main_gui.py`** - Tkinter GUI application (default mode)
- **`src/core/audio_summarizer.py`** - CLI interface for single file processing
- **`src/core/batch_process.py`** - CLI interface for batch folder processing

### Core Components

| Module | Class | Responsibility |
|--------|-------|-----------------|
| `src/config/config_manager.py` | `ConfigManager` | Manages INI-based configuration (API keys, defaults) via `src/config/config.ini` |
| `src/core/whisper_transcriber.py` | `WhisperTranscriber` | Wraps OpenAI Whisper model for speech-to-text |
| `src/core/deepseek_summarizer.py` | `DeepSeekSummarizer` | Calls DeepSeek API for content summarization |
| `src/utils/file_utils.py` | `FileUtils` | File I/O, path handling, result saving |

### Data Flow

```
Audio File -> WhisperTranscriber -> Transcription Text
                                                    |
                                                    v
                                    DeepSeekSummarizer -> Summary Text
                                                    |
                                                    v
                                    FileUtils -> Save to disk
                                                    |
                                    +---------------+---------------+
                                    |                               |
                            transcripts/                    summaries/
```

### GUI Threading Architecture

The GUI uses a producer-consumer pattern with two worker pools:
1. **Single transcription thread** (CPU-intensive Whisper model) - only one at a time
2. **Thread pool of 5 summary threads** (I/O-intensive API calls) - concurrent

Files progress through: `transcription_queue` -> `summary_queue` -> disk

## Configuration

Configuration is stored in `src/config/config.ini`:

```ini
[api]
api_key = sk-xxxxxxxxxxxx

[settings]
default_model = small          # Options: tiny, base, small, medium, large
default_template = audio_content_analysis
output_folder = C:/path/to/output
```

Run `python main.py --config` to set these values interactively.

### External Dependencies

- **FFmpeg** - Required for video audio extraction (path configurable in extraction tool)
- **CUDA** - Optional, for GPU acceleration (auto-detected by PyTorch)
- **DeepSeek API Key** - Required for summarization features

## Prompt Templates

The `prompts/` directory contains AI prompt templates used by DeepSeekSummarizer. Templates use Python `.format()` style variable substitution:

| Template | Variables | Purpose |
|----------|-----------|---------|
| `audio_content_analysis.txt` | `{audio_title}`, `{content}` | Deep audio analysis (default) |
| `course_analysis.txt` | `{course_title}`, `{instructor}`, `{duration}`, `{content}` | Course/lecture analysis |
| `meeting_analysis.txt` | `{meeting_title}`, `{meeting_time}`, `{attendees}`, `{content}` | Meeting analysis |
| `text_summary.txt` | `{title}`, `{content}` | Generic summary |

**Note**: Templates use Python `.format()` style variable substitution. Some templates require additional metadata (like `instructor`, `duration` for course analysis) that is not automatically collected by the application - these must be manually edited in the template or passed when using the API directly.

Templates are UTF-8 encoded text files. To add a new template, create a `.txt` file and reference it by name (without extension) in the `--template` argument.

## Key Patterns

### Path Handling
- Uses `os.path` for cross-platform compatibility
- Configuration uses Windows-style paths (`C:/path/to/output`)
- All text files use UTF-8 encoding

### Output File Naming
- Transcriptions: `{basename}_转录_{timestamp}.txt`
- Summaries: `{basename}_总结{timestamp}.md`

### Progress Tracking
- Callback-based progress reporting for GUI integration
- Stop flags (`_stop_flag` attributes) for graceful cancellation
- GUI uses `progress_callback` for real-time progress updates during transcription

### Batch Processing
- Preserves source folder hierarchy in output directory
- Processes all supported audio formats in source tree recursively
- Supports `--threads` parameter for concurrent processing (default: varies by mode)

## Language Notes

- The codebase contains Chinese comments, UI text, and documentation
- Output filenames use Chinese characters: `转录` (transcription), `总结` (summary)
- User-facing messages are in Chinese
