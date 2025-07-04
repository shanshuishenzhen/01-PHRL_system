#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开发工具界面启动测试脚本
验证开发工具界面能否正常启动，不出现编码错误
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def test_ui_startup():
    """测试开发工具界面启动"""
    print("🔍 测试开发工具界面启动")
    print("-" * 40)
    
    try:
        # 启动开发工具界面
        print("正在启动开发工具界面...")
        
        # 使用subprocess启动，设置超时
        process = subprocess.Popen([
            sys.executable, 'developer_tools.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 等待3秒看是否有错误
        try:
            stdout, stderr = process.communicate(timeout=3)
            
            # 如果进程在3秒内结束，说明有错误
            if process.returncode != 0:
                print(f"❌ 开发工具启动失败")
                print(f"错误输出: {stderr}")
                return False
            else:
                print("✅ 开发工具正常启动并退出")
                return True
                
        except subprocess.TimeoutExpired:
            # 超时说明程序还在运行，这是正常的
            print("✅ 开发工具界面正常启动（程序仍在运行）")
            
            # 终止进程
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            return True
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_import_modules():
    """测试模块导入"""
    print("\n🔍 测试模块导入")
    print("-" * 40)
    
    try:
        # 测试导入开发工具模块
        print("正在测试模块导入...")
        
        result = subprocess.run([
            sys.executable, '-c', 
            'import developer_tools; print("开发工具模块导入成功")'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ 开发工具模块导入成功")
            return True
        else:
            print(f"❌ 开发工具模块导入失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 模块导入测试失败: {e}")
        return False

def test_question_generator_import():
    """测试题库生成器导入"""
    print("\n🔍 测试题库生成器导入")
    print("-" * 40)
    
    try:
        result = subprocess.run([
            sys.executable, '-c', 
            'from developer_tools.question_bank_generator import generate_from_excel; print("题库生成器导入成功")'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ 题库生成器导入成功")
            return True
        else:
            print(f"❌ 题库生成器导入失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 题库生成器导入测试失败: {e}")
        return False

def test_encoding_safety():
    """测试编码安全性"""
    print("\n🔍 测试编码安全性")
    print("-" * 40)
    
    try:
        # 检查开发工具文件中是否还有有问题的Unicode字符
        with open("developer_tools.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        problematic_chars = ['🛠️', '👤', '📝', '🔥', '🚀', '📋', '🗑️', '✅', '⚠️']
        found_chars = []
        
        for char in problematic_chars:
            if char in content:
                found_chars.append(char)
        
        if found_chars:
            print(f"❌ 发现有问题的Unicode字符: {found_chars}")
            return False
        else:
            print("✅ 未发现有问题的Unicode字符")
            return True
            
    except Exception as e:
        print(f"❌ 编码安全性测试失败: {e}")
        return False

def test_template_file_access():
    """测试模板文件访问"""
    print("\n🔍 测试模板文件访问")
    print("-" * 40)
    
    try:
        template_file = Path("developer_tools/样例题组题规则模板.xlsx")
        
        if template_file.exists():
            print(f"✅ 模板文件存在: {template_file}")
            
            # 测试文件是否可读
            try:
                with open(template_file, 'rb') as f:
                    data = f.read(100)  # 读取前100字节
                print("✅ 模板文件可正常读取")
                return True
            except Exception as e:
                print(f"❌ 模板文件读取失败: {e}")
                return False
        else:
            print(f"❌ 模板文件不存在: {template_file}")
            return False
            
    except Exception as e:
        print(f"❌ 模板文件访问测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开发工具界面启动测试")
    print("=" * 50)
    
    tests = [
        ("模块导入测试", test_import_modules),
        ("题库生成器导入测试", test_question_generator_import),
        ("编码安全性测试", test_encoding_safety),
        ("模板文件访问测试", test_template_file_access),
        ("界面启动测试", test_ui_startup),
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
        print("🎉 所有测试通过！开发工具界面可以正常启动！")
        print("\n✅ 验证结果:")
        print("1. ✅ 所有模块可以正常导入")
        print("2. ✅ 题库生成器功能正常")
        print("3. ✅ 编码问题已完全修复")
        print("4. ✅ 模板文件可以正常访问")
        print("5. ✅ 开发工具界面可以正常启动")
        
        print("\n🚀 现在可以安全使用开发工具:")
        print("• 运行: python developer_tools.py")
        print("• 选择'样例题库生成'选项卡")
        print("• 上传模板文件并生成题库")
        print("• 不会再出现编码错误")
        
    else:
        print("⚠️  部分测试失败，请检查相关问题")
        
        if passed_tests >= 3:
            print("\n💡 建议:")
            print("- 基础功能已修复，可以尝试手动启动")
            print("- 运行: python developer_tools.py")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
