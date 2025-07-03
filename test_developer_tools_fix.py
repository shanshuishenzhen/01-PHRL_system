#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开发工具修复验证脚本
测试开发工具模块的启动和功能
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def test_developer_tools_file():
    """测试开发工具文件是否存在"""
    print("🔍 测试1: 检查开发工具文件")
    print("-" * 40)
    
    developer_tools_path = Path("developer_tools.py")
    if developer_tools_path.exists():
        print(f"✅ 开发工具文件存在: {developer_tools_path}")
        
        # 检查文件内容
        try:
            with open(developer_tools_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "class DeveloperTools" in content:
                print("✅ 开发工具类定义存在")
            else:
                print("❌ 开发工具类定义不存在")
                return False
                
            if "数据生成助手" in content:
                print("✅ 开发工具界面标题正确")
            else:
                print("❌ 开发工具界面标题不正确")
                return False
                
            return True
        except Exception as e:
            print(f"❌ 读取开发工具文件失败: {e}")
            return False
    else:
        print(f"❌ 开发工具文件不存在: {developer_tools_path}")
        return False

def test_main_console_integration():
    """测试主控台集成"""
    print("\n🔍 测试2: 主控台集成检查")
    print("-" * 40)
    
    try:
        with open("main_console.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查开发工具模块状态定义
        if '"developer_tools": {"status": "未启动"' in content:
            print("✅ 开发工具模块状态已定义")
        else:
            print("❌ 开发工具模块状态未定义")
            return False
        
        # 检查开发工具按钮定义
        if '"开发工具", "key": "developer_tools"' in content:
            print("✅ 开发工具按钮已定义")
        else:
            print("❌ 开发工具按钮未定义")
            return False
        
        # 检查启动函数
        if "def start_developer_tools(self):" in content:
            print("✅ 开发工具启动函数已定义")
            
            # 检查是否还显示"开发中"
            if "开发工具功能开发中" in content:
                print("❌ 仍显示'开发工具功能开发中'")
                return False
            else:
                print("✅ 已移除'开发中'提示")
        else:
            print("❌ 开发工具启动函数未定义")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 检查主控台集成失败: {e}")
        return False

def test_launcher_integration():
    """测试启动器集成"""
    print("\n🔍 测试3: 启动器集成检查")
    print("-" * 40)
    
    try:
        with open("launcher.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查模块状态定义
        if '"developer_tools": {' in content:
            print("✅ 启动器中开发工具模块状态已定义")
        else:
            print("❌ 启动器中开发工具模块状态未定义")
            return False
        
        # 检查按钮定义
        if 'developer_tools_btn' in content:
            print("✅ 启动器中开发工具按钮已定义")
        else:
            print("❌ 启动器中开发工具按钮未定义")
            return False
        
        # 检查启动函数
        if "def start_developer_tools(self):" in content:
            print("✅ 启动器中开发工具启动函数已定义")
        else:
            print("❌ 启动器中开发工具启动函数未定义")
            return False
        
        # 检查模块列表
        if '"developer_tools"' in content and '"开发工具"' in content:
            print("✅ 开发工具已添加到模块列表")
        else:
            print("❌ 开发工具未添加到模块列表")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 检查启动器集成失败: {e}")
        return False

def test_direct_startup():
    """测试直接启动开发工具"""
    print("\n🔍 测试4: 直接启动开发工具")
    print("-" * 40)
    
    try:
        # 尝试启动开发工具（3秒后终止）
        print("启动开发工具...")
        process = subprocess.Popen([
            sys.executable, "developer_tools.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 等待3秒让程序启动
        time.sleep(3)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("✅ 开发工具成功启动")
            
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
            print(f"❌ 开发工具启动失败")
            if stderr:
                print(f"错误信息: {stderr[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ 直接启动测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖检查"""
    print("\n🔍 测试5: 依赖检查")
    print("-" * 40)
    
    required_modules = ['tkinter', 'openpyxl', 'pandas']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - 未安装")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️  缺少依赖: {', '.join(missing_modules)}")
        return False
    else:
        print("\n✅ 所有依赖都已安装")
        return True

def main():
    """主测试函数"""
    print("🧪 开发工具修复验证测试")
    print("=" * 50)
    
    tests = [
        ("开发工具文件检查", test_developer_tools_file),
        ("主控台集成检查", test_main_console_integration),
        ("启动器集成检查", test_launcher_integration),
        ("直接启动测试", test_direct_startup),
        ("依赖检查", test_dependencies)
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
        print("🎉 所有测试通过！开发工具修复成功！")
        print("\n✅ 现在可以:")
        print("1. 运行 python launcher.py")
        print("2. 点击'开发工具'按钮启动")
        print("3. 或运行 python main_console.py")
        print("4. 点击'开发工具'模块启动")
        print("5. 或直接运行 python developer_tools.py")
        
        print("\n🔧 修复内容:")
        print("- 修复了主控台中开发工具的启动函数")
        print("- 移除了'开发工具功能开发中'的提示")
        print("- 在启动器中添加了开发工具模块")
        print("- 添加了开发工具的状态监控")
        print("- 实现了完整的启动和管理功能")
    else:
        print("⚠️  部分测试失败，请检查相关问题")
        
        if passed_tests >= 3:
            print("\n💡 建议:")
            print("- 基础功能正常，可以尝试手动启动")
            print("- 运行: python developer_tools.py")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
