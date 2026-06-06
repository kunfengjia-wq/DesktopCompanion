@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title 桌面伴侣
echo ================================
echo   桌面伴侣 - AI Desktop Companion
echo ================================
echo.

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

REM 检查依赖
echo [启动] 检查依赖...
python -c "import PyQt6" 2>nul
if %errorlevel% neq 0 (
    echo [安装] 正在安装依赖...
    pip install -r requirements.txt
)

echo [启动] 正在启动桌面伴侣...
python main.py

pause
