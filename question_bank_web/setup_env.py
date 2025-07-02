#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库管理模块独立虚拟环境设置脚本

解决numpy导入冲突问题，为题库管理模块创建独立的虚拟环境。

更新日志：
- 2025-01-07：创建独立虚拟环境设置脚本
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def create_virtual_environment():
    """创建独立的虚拟环境"""
    current_dir = Path(__file__).parent
    venv_dir = current_dir / "venv_qb"
    
    print("🔧 正在为题库管理模块创建独立虚拟环境...")
    
    # 检查是否已存在虚拟环境
    if venv_dir.exists():
        print(f"✅ 虚拟环境已存在: {venv_dir}")
        return venv_dir
    
    try:
        # 创建虚拟环境
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        print(f"✅ 虚拟环境创建成功: {venv_dir}")
        return venv_dir
    except subprocess.CalledProcessError as e:
        print(f"❌ 虚拟环境创建失败: {e}")
        return None


def get_pip_executable(venv_dir):
    """获取虚拟环境中的pip可执行文件路径"""
    if platform.system() == "Windows":
        return venv_dir / "Scripts" / "pip.exe"
    else:
        return venv_dir / "bin" / "pip"


def install_dependencies(venv_dir):
    """在虚拟环境中安装依赖"""
    pip_exe = get_pip_executable(venv_dir)
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt 文件不存在，创建默认依赖文件...")
        create_requirements_file(requirements_file)
    
    print("📦 正在安装依赖包...")
    
    # 升级pip
    try:
        subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], check=True)
        print("✅ pip 升级成功")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ pip 升级失败: {e}")
    
    # 安装依赖
    try:
        subprocess.run([str(pip_exe), "install", "-r", str(requirements_file)], check=True)
        print("✅ 依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False


def create_requirements_file(requirements_file):
    """创建题库管理模块的requirements.txt文件"""
    requirements_content = """# 题库管理模块依赖包
# 解决numpy导入冲突的独立环境

# Web框架
Flask==2.3.3
Flask-CORS==3.0.10
Flask-SQLAlchemy==2.5.1
Werkzeug==3.0.3

# 数据库
SQLAlchemy==2.0.41

# 数据处理（独立安装避免冲突）
numpy==1.26.4
pandas==2.3.0
openpyxl==3.1.4

# 其他依赖
Jinja2==3.1.4
MarkupSafe==2.1.5
click==8.1.7
itsdangerous==2.2.0
"""
    
    with open(requirements_file, 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    
    print(f"✅ 创建 requirements.txt 文件: {requirements_file}")


def create_activation_script():
    """创建虚拟环境激活脚本"""
    current_dir = Path(__file__).parent
    
    if platform.system() == "Windows":
        # Windows 批处理脚本
        script_content = """@echo off
echo 激活题库管理模块虚拟环境...
call venv_qb\\Scripts\\activate.bat
echo 虚拟环境已激活，可以运行 python app.py 启动题库管理模块
cmd /k
"""
        script_file = current_dir / "activate_env.bat"
    else:
        # Linux/Mac shell脚本
        script_content = """#!/bin/bash
echo "激活题库管理模块虚拟环境..."
source venv_qb/bin/activate
echo "虚拟环境已激活，可以运行 python app.py 启动题库管理模块"
bash
"""
        script_file = current_dir / "activate_env.sh"
    
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 给shell脚本添加执行权限
    if platform.system() != "Windows":
        os.chmod(script_file, 0o755)
    
    print(f"✅ 创建激活脚本: {script_file}")


def create_run_script():
    """创建运行脚本"""
    current_dir = Path(__file__).parent
    
    if platform.system() == "Windows":
        # Windows 批处理脚本
        script_content = """@echo off
echo 启动题库管理模块...
call venv_qb\\Scripts\\activate.bat
python app.py
pause
"""
        script_file = current_dir / "run_app.bat"
    else:
        # Linux/Mac shell脚本
        script_content = """#!/bin/bash
echo "启动题库管理模块..."
source venv_qb/bin/activate
python app.py
"""
        script_file = current_dir / "run_app.sh"
    
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 给shell脚本添加执行权限
    if platform.system() != "Windows":
        os.chmod(script_file, 0o755)
    
    print(f"✅ 创建运行脚本: {script_file}")


def main():
    """主函数"""
    print("🚀 题库管理模块独立虚拟环境设置")
    print("=" * 50)
    
    # 创建虚拟环境
    venv_dir = create_virtual_environment()
    if not venv_dir:
        print("❌ 虚拟环境创建失败，退出")
        return False
    
    # 安装依赖
    if not install_dependencies(venv_dir):
        print("❌ 依赖安装失败，退出")
        return False
    
    # 创建脚本
    create_activation_script()
    create_run_script()
    
    print("\n✅ 题库管理模块独立虚拟环境设置完成！")
    print("\n📋 使用说明：")
    if platform.system() == "Windows":
        print("1. 激活环境: 双击 activate_env.bat")
        print("2. 运行模块: 双击 run_app.bat")
    else:
        print("1. 激活环境: ./activate_env.sh")
        print("2. 运行模块: ./run_app.sh")
    print("3. 手动运行: 激活环境后执行 python app.py")
    
    return True


if __name__ == "__main__":
    main()
