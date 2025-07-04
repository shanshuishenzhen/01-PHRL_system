#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PH&RL 在线考试系统 - 依赖检查脚本
检查所有必要的Python和Node.js依赖是否正确安装
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    print(f"   Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("   ❌ Python版本过低，需要Python 3.6+")
        return False
    else:
        print("   ✅ Python版本符合要求")
        return True

def check_python_packages():
    """检查关键Python包"""
    print("\n📦 检查Python依赖包...")
    
    critical_packages = [
        'flask', 'pandas', 'numpy', 'sqlalchemy', 
        'requests', 'openpyxl', 'bcrypt', 'jwt'
    ]
    
    missing_packages = []
    
    for package in critical_packages:
        try:
            if package == 'jwt':
                importlib.import_module('jwt')
            else:
                importlib.import_module(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - 未安装")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_nodejs():
    """检查Node.js环境"""
    print("\n🟢 检查Node.js环境...")

    try:
        # 检查Node.js版本
        result = subprocess.run(['node', '--version'],
                              capture_output=True, text=True, check=True, shell=True)
        node_version = result.stdout.strip()
        print(f"   Node.js版本: {node_version}")

        # 检查npm版本
        result = subprocess.run(['npm', '--version'],
                              capture_output=True, text=True, check=True, shell=True)
        npm_version = result.stdout.strip()
        print(f"   npm版本: {npm_version}")

        print("   ✅ Node.js环境正常")
        return True

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"   ❌ Node.js检查失败: {e}")
        return False

def check_node_modules():
    """检查Node.js模块安装情况"""
    print("\n📦 检查Node.js模块...")
    
    modules_to_check = [
        ('user_management', ['express', 'mysql2', 'bcrypt', 'jsonwebtoken']),
        ('grading_center', ['jest', 'supertest'])
    ]
    
    all_good = True
    
    for module_dir, packages in modules_to_check:
        if os.path.exists(module_dir):
            print(f"   检查 {module_dir}...")
            node_modules_path = os.path.join(module_dir, 'node_modules')
            
            if os.path.exists(node_modules_path):
                for package in packages:
                    package_path = os.path.join(node_modules_path, package)
                    if os.path.exists(package_path):
                        print(f"     ✅ {package}")
                    else:
                        print(f"     ❌ {package} - 未安装")
                        all_good = False
            else:
                print(f"     ❌ node_modules目录不存在")
                all_good = False
        else:
            print(f"   ⚠️  {module_dir} 目录不存在")
    
    return all_good

def check_database_files():
    """检查数据库文件"""
    print("\n🗄️  检查数据库文件...")
    
    db_files = ['database.sqlite']
    
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"   ✅ {db_file}")
        else:
            print(f"   ⚠️  {db_file} - 不存在（首次运行时会自动创建）")

def check_config_files():
    """检查配置文件"""
    print("\n⚙️  检查配置文件...")
    
    config_files = [
        'config.json',
        'question_bank_web/requirements.txt',
        'user_management/package.json',
        'grading_center/package.json'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"   ✅ {config_file}")
        else:
            print(f"   ❌ {config_file} - 不存在")

def main():
    """主函数"""
    print("=" * 60)
    print("    PH&RL 在线考试系统 - 依赖环境检查")
    print("=" * 60)
    
    checks = [
        check_python_version(),
        check_python_packages(),
        check_nodejs(),
        check_node_modules()
    ]
    
    # 非关键检查
    check_database_files()
    check_config_files()
    
    print("\n" + "=" * 60)
    
    if all(checks):
        print("🎉 所有关键依赖检查通过！系统可以正常运行。")
        print("\n启动建议:")
        print("1. 运行 activate_env.bat 激活环境")
        print("2. 运行 python launcher.py 启动系统")
    else:
        print("❌ 发现依赖问题，请检查上述错误信息。")
        print("\n修复建议:")
        print("1. 激活虚拟环境: .\\venv\\Scripts\\activate")
        print("2. 安装Python依赖: pip install -r requirements.txt")
        print("3. 安装Node.js依赖: cd user_management && npm install")
        print("4. 安装Node.js依赖: cd grading_center && npm install")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
