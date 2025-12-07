@echo off
chcp 65001 > nul
title 视频音频提取工具

echo 启动视频音频提取工具GUI...
python extract_audio_gui.py

if %errorlevel% neq 0 (
    echo.
    echo 错误: 无法启动GUI工具
    echo 请确保Python已正确安装，并且extract_audio_gui.py文件在当前目录中
    pause
)