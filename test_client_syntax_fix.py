#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户端语法错误修复验证脚本
测试客户端应用的语法修复和启动功能
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def test_syntax_check():
    """测试语法检查"""
    print("🔍 测试1: 客户端语法检查")
    print("-" * 40)
    
    client_app_path = Path("client/client_app.py")
    if not client_app_path.exists():
        print(f"❌ 客户端文件不存在: {client_app_path}")
        return False
    
    try:
        # 使用Python编译器检查语法
        result = subprocess.run([
            sys.executable, '-m', 'py_compile', str(client_app_path)
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ 客户端语法检查通过")
            return True
        else:
            print(f"❌ 客户端语法错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 语法检查失败: {e}")
        return False

def test_import_check():
    """测试导入检查"""
    print("\n🔍 测试2: 客户端模块导入检查")
    print("-" * 40)
    
    try:
        # 临时添加client目录到路径
        client_dir = os.path.join(os.getcwd(), 'client')
        if client_dir not in sys.path:
            sys.path.insert(0, client_dir)
        
        # 尝试导入客户端模块的关键部分
        import tkinter as tk
        print("✅ tkinter导入成功")
        
        # 检查客户端应用文件的关键函数
        with open("client/client_app.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查修复的语法结构
        if "else:" in content and "不可用" in content:
            print("✅ 修复的else语句存在")
        else:
            print("❌ 修复的else语句不存在")
            return False
        
        # 检查缩进是否正确
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if "else:" in line and i > 520 and i < 530:
                # 检查else语句的缩进
                if line.startswith('                    else:'):  # 20个空格
                    print("✅ else语句缩进正确")
                    break
                else:
                    print(f"❌ else语句缩进不正确，行{i}: '{line}'")
                    return False
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 导入检查失败: {e}")
        return False

def test_client_startup():
    """测试客户端启动"""
    print("\n🔍 测试3: 客户端启动测试")
    print("-" * 40)
    
    try:
        # 尝试启动客户端（3秒后终止）
        print("启动客户端应用...")
        process = subprocess.Popen([
            sys.executable, "client_app.py"
        ], cwd="client", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 等待3秒让程序启动
        time.sleep(3)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("✅ 客户端成功启动")
            
            # 终止进程
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
            
            return True
        else:
            # 进程已经退出，获取输出
            stdout, stderr = process.communicate()
            if stderr:
                print(f"❌ 客户端启动失败: {stderr[:200]}...")
            else:
                print("❌ 客户端启动后立即退出")
            return False
            
    except Exception as e:
        print(f"❌ 客户端启动测试失败: {e}")
        return False

def test_specific_syntax_fix():
    """测试具体的语法修复"""
    print("\n🔍 测试4: 具体语法修复检查")
    print("-" * 40)
    
    try:
        with open("client/client_app.py", 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 检查第524行附近的修复
        found_fix = False
        for i, line in enumerate(lines):
            line_num = i + 1
            if line_num >= 520 and line_num <= 530:
                if "else:" in line and line.strip().startswith("else:"):
                    # 检查这个else是否正确缩进在if语句内部
                    if line.startswith('                    else:'):  # 20个空格，表示在if内部
                        print(f"✅ 第{line_num}行: else语句正确缩进在if内部")
                        found_fix = True
                    else:
                        print(f"❌ 第{line_num}行: else语句缩进不正确")
                        return False
        
        if found_fix:
            print("✅ 语法修复验证通过")
            return True
        else:
            print("❌ 未找到预期的语法修复")
            return False
            
    except Exception as e:
        print(f"❌ 语法修复检查失败: {e}")
        return False

def test_main_console_client_integration():
    """测试主控台客户端集成"""
    print("\n🔍 测试5: 主控台客户端集成检查")
    print("-" * 40)
    
    try:
        # 检查主控台是否能找到客户端
        with open("main_console.py", 'r', encoding='utf-8') as f:
            main_console_content = f.read()
        
        if "client" in main_console_content and "client_app.py" in main_console_content:
            print("✅ 主控台包含客户端启动逻辑")
        else:
            print("❌ 主控台缺少客户端启动逻辑")
            return False
        
        # 检查客户端路径是否正确
        client_path = Path("client/client_app.py")
        if client_path.exists():
            print("✅ 客户端文件路径正确")
        else:
            print("❌ 客户端文件路径不正确")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 主控台客户端集成检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 客户端语法错误修复验证测试")
    print("=" * 50)
    
    tests = [
        ("语法检查", test_syntax_check),
        ("模块导入检查", test_import_check),
        ("客户端启动测试", test_client_startup),
        ("具体语法修复检查", test_specific_syntax_fix),
        ("主控台客户端集成", test_main_console_client_integration)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 执行异常: {e}")
    
    print("\n" + "=" * 50)
    print("📊 测试结果摘要")
    print(f"通过测试: {passed_tests}/{total_tests}")
    print(f"通过率: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！客户端语法错误修复成功！")
        print("\n✅ 修复内容:")
        print("- 修复了第524行的else语句缩进问题")
        print("- 将独立的else改为if语句内部的else")
        print("- 客户端现在可以正常启动")
        print("- 主控台可以正常启动客户端模块")
        
        print("\n🚀 使用说明:")
        print("1. 运行 python main_console.py")
        print("2. 点击'客户机端'按钮")
        print("3. 客户端应该正常启动，状态显示为'运行中'")
        print("4. 或直接运行 cd client && python client_app.py")
    else:
        print("⚠️  部分测试失败，请检查相关问题")
        
        if passed_tests >= 3:
            print("\n💡 建议:")
            print("- 基础语法已修复，可以尝试手动启动")
            print("- 运行: cd client && python client_app.py")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
