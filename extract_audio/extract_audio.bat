@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: 视频音频提取批处理脚本
:: 使用FFmpeg从视频文件中提取音频，并保持源文件夹结构

set "FFMPEG_PATH=D:\software\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe"

:: 检查FFmpeg是否存在
if not exist "%FFMPEG_PATH%" (
    echo 错误: FFmpeg未找到于路径 %FFMPEG_PATH%
    pause
    exit /b 1
)

:: 获取输入参数
if "%~1"=="" (
    echo 用法: %~nx0 源文件夹路径 目标文件夹路径
    echo 示例: %~nx0 "D:\Videos" "D:\Audio"
    pause
    exit /b 1
)

if "%~2"=="" (
    echo 用法: %~nx0 源文件夹路径 目标文件夹路径
    echo 示例: %~nx0 "D:\Videos" "D:\Audio"
    pause
    exit /b 1
)

set "SOURCE_DIR=%~1"
set "TARGET_DIR=%~2"

:: 检查源目录是否存在
if not exist "%SOURCE_DIR%" (
    echo 错误: 源目录不存在: %SOURCE_DIR%
    pause
    exit /b 1
)

:: 创建目标目录
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo 正在扫描视频文件...
set /a count=0

:: 递归处理所有视频文件
for /r "%SOURCE_DIR%" %%f in (*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm *.m4v *.3gp) do (
    set /a count+=1
    set "input_file=%%f"
    
    :: 计算相对路径
    call :GetRelativePath "!input_file!" "%SOURCE_DIR%" rel_path
    
    :: 更改扩展名为.wav
    set "output_path=%TARGET_DIR%\!rel_path!"
    set "output_dir=!output_path:\%%~nxf=!"
    set "output_file=!output_dir!\%%~nf.wav"
    
    :: 创建目标目录结构
    if not exist "!output_dir!" mkdir "!output_dir!"
    
    echo 正在处理: !input_file!
    echo 输出: !output_file!
    
    :: 检查输出文件是否已存在
    if exist "!output_file!" (
        echo 跳过已存在的文件: !output_file!
    ) else (
        :: 使用FFmpeg提取音频
        "%FFMPEG_PATH%" -i "!input_file!" -vn -acodec pcm_s16le -ar 16000 -ac 1 -y "!output_file!" >nul 2>&1
        
        if !errorlevel! equ 0 (
            echo 成功: !output_file!
        ) else (
            echo 失败: !input_file!
        )
    )
)

echo.
echo 处理完成! 共处理了 %count% 个视频文件
pause
exit /b 0

:: 获取相对路径的函数
:GetRelativePath
set "full_path=%~1"
set "base_path=%~2"

:: 替换反斜杠为正斜杠以便处理
set "full_path=!full_path:\=/!"
set "base_path=!base_path:\=/!"

:: 计算相对路径
call set "rel_path=%%full_path:*!base_path!/=%%"

:: 替换回反斜杠
set "rel_path=!rel_path:/=\!"

:: 设置返回值
set "%~3=!rel_path!"
goto :eof