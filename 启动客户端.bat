@echo off
chcp 65001 >nul
title PH&RL 考试系统 - 独立客户端启动器

echo.
echo ========================================
echo    PH&RL 考试系统 - 独立客户端
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python环境
    echo 请确保已安装Python并添加到系统PATH
    echo.
    pause
    exit /b 1
)

:: 检查客户端文件是否存在
if not exist "standalone_client.py" (
    echo ❌ 错误：未找到客户端文件 standalone_client.py
    echo 请确保在正确的目录中运行此脚本
    echo.
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo ✅ 客户端文件检查通过
echo.
echo 🚀 正在启动独立客户端...
echo.

:: 启动客户端
python standalone_client.py

:: 如果客户端异常退出，显示错误信息
if errorlevel 1 (
    echo.
    echo ❌ 客户端异常退出，错误代码: %errorlevel%
    echo 请检查日志文件 standalone_client.log 获取详细信息
    echo.
    pause
)

echo.
echo 客户端已关闭
pause
