#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户端启动测试脚本
验证客户端的各种启动方式
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def test_launcher_dependency_check():
    """测试启动器依赖检查（不实际启动GUI）"""
    print("🔍 测试1: 启动器Pillow依赖检查")
    print("-" * 40)
    
    try:
        # 运行启动器的依赖检查
        result = subprocess.run([
            sys.executable, "launcher.py", "--check-only"
        ], capture_output=True, text=True, timeout=30, cwd=".")
        
        output = result.stdout + result.stderr
        
        # 检查关键信息
        if "pillow库已安装 (导入为 PIL)" in output:
            print("✅ Pillow依赖检查修复成功")
            return True
        elif "Pillow库未安装" in output:
            print("❌ Pillow依赖检查仍有问题")
            return False
        else:
            print("⚠️  无法确定Pillow依赖状态")
            print(f"输出: {output[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  启动器检查超时")
        return False
    except Exception as e:
        print(f"❌ 启动器测试失败: {e}")
        return False

def test_standalone_launcher():
    """测试独立启动器（快速启动测试）"""
    print("\n🔍 测试2: 独立启动器功能")
    print("-" * 40)
    
    try:
        # 快速测试独立启动器（3秒后终止）
        process = subprocess.Popen([
            sys.executable, "client/standalone_launcher.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
        text=True, cwd=".")
        
        # 等待3秒让程序启动
        time.sleep(3)
        
        # 终止进程
        process.terminate()
        
        # 获取输出
        try:
            stdout, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        
        output = stdout + stderr
        
        # 检查关键信息
        success_indicators = [
            "独立运行模式，跳过主控台检查",
            "客户端界面已加载",
            "获取到 12 个考试"
        ]
        
        passed_checks = 0
        for indicator in success_indicators:
            if indicator in output:
                print(f"✅ {indicator}")
                passed_checks += 1
            else:
                print(f"❌ 未找到: {indicator}")
        
        if passed_checks >= 2:
            print("✅ 独立启动器工作正常")
            return True
        else:
            print("❌ 独立启动器存在问题")
            print(f"输出: {output[:300]}...")
            return False
            
    except Exception as e:
        print(f"❌ 独立启动器测试失败: {e}")
        return False

def test_direct_client_startup():
    """测试直接启动客户端应用"""
    print("\n🔍 测试3: 直接启动客户端应用")
    print("-" * 40)
    
    try:
        # 快速测试直接启动（3秒后终止）
        process = subprocess.Popen([
            sys.executable, "client/client_app.py", "--standalone"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
        text=True, cwd=".")
        
        # 等待3秒让程序启动
        time.sleep(3)
        
        # 终止进程
        process.terminate()
        
        # 获取输出
        try:
            stdout, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        
        output = stdout + stderr
        
        # 检查关键信息
        success_indicators = [
            "独立运行模式已启用",
            "客户端界面已加载",
            "获取到 12 个考试"
        ]
        
        passed_checks = 0
        for indicator in success_indicators:
            if indicator in output:
                print(f"✅ {indicator}")
                passed_checks += 1
            else:
                print(f"❌ 未找到: {indicator}")
        
        if passed_checks >= 2:
            print("✅ 直接启动客户端工作正常")
            return True
        else:
            print("❌ 直接启动客户端存在问题")
            print(f"输出: {output[:300]}...")
            return False
            
    except Exception as e:
        print(f"❌ 直接启动客户端测试失败: {e}")
        return False

def test_file_existence():
    """测试必要文件是否存在"""
    print("\n🔍 测试4: 必要文件检查")
    print("-" * 40)
    
    required_files = [
        "launcher.py",
        "client/client_app.py", 
        "client/standalone_launcher.py",
        "client/api.py",
        "client/available_exams.json"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  缺少文件: {', '.join(missing_files)}")
        return False
    else:
        print("\n✅ 所有必要文件存在")
        return True

def main():
    """主测试函数"""
    print("🧪 客户端启动功能测试")
    print("=" * 50)
    print("注意: 此测试会启动GUI应用，3秒后自动终止")
    print("=" * 50)
    
    tests = [
        ("启动器Pillow依赖检查", test_launcher_dependency_check),
        ("独立启动器功能", test_standalone_launcher),
        ("直接启动客户端应用", test_direct_client_startup),
        ("必要文件检查", test_file_existence)
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
        print("🎉 所有测试通过！客户端启动问题已完全修复！")
        print("\n✅ 现在可以使用以下方式启动客户端:")
        print("1. python launcher.py                    # 完整系统启动")
        print("2. python client/standalone_launcher.py  # 独立启动器")
        print("3. python client/client_app.py --standalone  # 直接启动")
    else:
        print("⚠️  部分测试失败，请检查相关问题")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
