@echo off
echo ========================================
echo PH^&RL 在线考试系统 GitHub 上传脚本
echo ========================================
echo.

echo 检查Git状态...
git status
if %errorlevel% neq 0 (
    echo 错误: 不是Git仓库或Git未安装
    pause
    exit /b 1
)

echo.
echo 检查远程仓库配置...
git remote -v
if %errorlevel% neq 0 (
    echo 添加远程仓库...
    git remote add origin https://github.com/shanshuishenzhen/01-PHRL_system.git
)

echo.
echo 设置主分支为main...
git branch -M main

echo.
echo 检查网络连接...
ping github.com -n 2
if %errorlevel% neq 0 (
    echo 警告: 无法连接到GitHub，请检查网络连接
    echo 您可以稍后重新运行此脚本
    pause
    exit /b 1
)

echo.
echo 开始推送到GitHub...
echo 注意: 如果提示输入用户名和密码，请使用GitHub用户名和Personal Access Token
echo.

git push -u origin main

if %errorlevel% eq 0 (
    echo.
    echo ========================================
    echo ✅ 成功上传到GitHub!
    echo ========================================
    echo.
    echo 仓库地址: https://github.com/shanshuishenzhen/01-PHRL_system
    echo.
    echo 上传内容包括:
    echo - 完整的PH^&RL在线考试系统代码
    echo - 智能阅卷系统和测试框架
    echo - API网关和系统监控
    echo - Docker部署配置
    echo - 详细的文档和使用指南
    echo.
) else (
    echo.
    echo ========================================
    echo ❌ 上传失败
    echo ========================================
    echo.
    echo 可能的原因:
    echo 1. 网络连接问题
    echo 2. 需要身份验证 (用户名/Personal Access Token)
    echo 3. 仓库权限问题
    echo.
    echo 解决方案:
    echo 1. 检查网络连接
    echo 2. 确保GitHub仓库存在且有写入权限
    echo 3. 使用Personal Access Token而不是密码
    echo.
    echo 手动推送命令:
    echo git push -u origin main
    echo.
)

echo 按任意键退出...
pause >nul
