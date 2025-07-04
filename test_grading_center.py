#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阅卷中心启动测试脚本
验证阅卷中心的启动修复
"""

import os
import sys
import subprocess
import time
import socket
from pathlib import Path

def check_port_available(port, host="127.0.0.1"):
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0
    except Exception:
        return False

def check_node_installed():
    """检查Node.js是否安装"""
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js已安装: {version}")
            return True
        else:
            print("❌ Node.js未正确安装")
            return False
    except Exception as e:
        print(f"❌ 检查Node.js时出错: {e}")
        return False

def check_npm_installed():
    """检查npm是否安装"""
    try:
        result = subprocess.run(['npm', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ npm已安装: {version}")
            return True
        else:
            print("❌ npm未正确安装")
            return False
    except Exception as e:
        print(f"❌ 检查npm时出错: {e}")
        return False

def check_grading_center_files():
    """检查阅卷中心文件结构"""
    print("\n🔍 检查阅卷中心文件结构...")
    
    required_files = [
        "grading_center/server/app.js",
        "grading_center/server/package.json",
        "grading_center/client/package.json",
        "grading_center/client/vite.config.js"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_dependencies_installed():
    """检查依赖是否安装"""
    print("\n🔍 检查依赖安装情况...")
    
    # 检查服务器端依赖
    server_node_modules = Path("grading_center/server/node_modules")
    if server_node_modules.exists():
        print("✅ 服务器端依赖已安装")
        server_deps_ok = True
    else:
        print("❌ 服务器端依赖未安装")
        server_deps_ok = False
    
    # 检查客户端依赖
    client_node_modules = Path("grading_center/client/node_modules")
    if client_node_modules.exists():
        print("✅ 客户端依赖已安装")
        client_deps_ok = True
    else:
        print("❌ 客户端依赖未安装")
        client_deps_ok = False
    
    return server_deps_ok and client_deps_ok

def install_dependencies():
    """安装依赖"""
    print("\n📦 安装阅卷中心依赖...")
    
    try:
        # 安装服务器端依赖
        print("安装服务器端依赖...")
        result = subprocess.run(['npm', 'install'], 
                              cwd='grading_center/server',
                              capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✅ 服务器端依赖安装成功")
        else:
            print(f"❌ 服务器端依赖安装失败: {result.stderr}")
            return False
        
        # 安装客户端依赖
        print("安装客户端依赖...")
        result = subprocess.run(['npm', 'install'], 
                              cwd='grading_center/client',
                              capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✅ 客户端依赖安装成功")
            return True
        else:
            print(f"❌ 客户端依赖安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 安装依赖时出错: {e}")
        return False

def test_grading_center_startup():
    """测试阅卷中心启动"""
    print("\n🚀 测试阅卷中心启动...")
    
    backend_port = 3000
    frontend_port = 5173
    
    # 检查端口是否可用
    if not check_port_available(backend_port):
        print(f"❌ 后端端口 {backend_port} 已被占用")
        return False
    
    if not check_port_available(frontend_port):
        print(f"❌ 前端端口 {frontend_port} 已被占用")
        return False
    
    print(f"✅ 端口检查通过 - 后端: {backend_port}, 前端: {frontend_port}")
    
    # 测试启动逻辑
    try:
        # 导入并测试启动函数
        sys.path.append('common')
        from process_manager import start_grading_center_module
        
        module_path = "grading_center/server/app.js"
        cwd = "grading_center/server"
        
        print("调用阅卷中心启动函数...")
        result = start_grading_center_module(module_path, cwd)
        
        print(f"启动结果: {result}")
        
        if result["status"] == "running":
            print("✅ 阅卷中心启动成功！")
            print(f"   后端PID: {result.get('backend_pid')}")
            print(f"   前端PID: {result.get('frontend_pid')}")
            print(f"   访问地址: {result.get('url')}")
            return True
        else:
            print(f"❌ 阅卷中心启动失败: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ 测试启动时出错: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 阅卷中心启动修复测试")
    print("=" * 50)
    
    tests = [
        ("Node.js环境检查", check_node_installed),
        ("npm环境检查", check_npm_installed),
        ("文件结构检查", check_grading_center_files),
        ("依赖安装检查", check_dependencies_installed)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        print("-" * 30)
        try:
            if test_func():
                passed_tests += 1
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 执行异常: {e}")
    
    # 如果依赖未安装，尝试安装
    if not check_dependencies_installed():
        print("\n📦 尝试安装缺失的依赖...")
        if install_dependencies():
            print("✅ 依赖安装成功")
            passed_tests += 1
        else:
            print("❌ 依赖安装失败")
    
    print("\n" + "=" * 50)
    print("📊 测试结果摘要")
    print(f"通过测试: {passed_tests}/{total_tests}")
    print(f"通过率: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 所有基础检查通过！")
        print("\n下一步:")
        print("1. 运行 python launcher.py")
        print("2. 点击启动阅卷中心")
        print("3. 浏览器应该自动打开 http://localhost:5173")
    else:
        print("⚠️  部分检查失败，请解决相关问题后重试")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
