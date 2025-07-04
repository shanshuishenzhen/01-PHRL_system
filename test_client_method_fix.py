#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户端方法修复验证脚本
测试ExamListView类中缺失方法的修复
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
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'py_compile', 'client/client_app.py'
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

def test_method_existence():
    """测试方法是否存在"""
    print("\n🔍 测试2: ExamListView类方法检查")
    print("-" * 40)
    
    try:
        with open("client/client_app.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查ExamListView类是否存在
        if "class ExamListView" not in content:
            print("❌ ExamListView类不存在")
            return False
        print("✅ ExamListView类存在")
        
        # 检查必要的方法是否在ExamListView类中
        required_methods = [
            "def view_exam_details",
            "def enter_exam_fullscreen", 
            "def enable_anti_cheat_mode",
            "def on_focus_lost",
            "def on_focus_gained",
            "def log_cheat_attempt"
        ]
        
        # 找到ExamListView类的开始和结束位置
        lines = content.split('\n')
        exam_list_view_start = -1
        exam_list_view_end = -1
        
        for i, line in enumerate(lines):
            if "class ExamListView" in line:
                exam_list_view_start = i
            elif exam_list_view_start != -1 and line.startswith("class ") and "ExamListView" not in line:
                exam_list_view_end = i
                break
        
        if exam_list_view_end == -1:
            exam_list_view_end = len(lines)
        
        if exam_list_view_start == -1:
            print("❌ 无法找到ExamListView类定义")
            return False
        
        # 检查方法是否在ExamListView类中
        exam_list_view_content = '\n'.join(lines[exam_list_view_start:exam_list_view_end])
        
        for method in required_methods:
            if method in exam_list_view_content:
                print(f"✅ {method} 方法存在于ExamListView类中")
            else:
                print(f"❌ {method} 方法不存在于ExamListView类中")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 方法检查失败: {e}")
        return False

def test_method_calls():
    """测试方法调用"""
    print("\n🔍 测试3: 方法调用检查")
    print("-" * 40)
    
    try:
        with open("client/client_app.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有调用enter_exam_fullscreen的地方
        if "self.enter_exam_fullscreen" in content:
            print("✅ enter_exam_fullscreen方法被正确调用")
        else:
            print("❌ enter_exam_fullscreen方法未被调用")
            return False
        
        # 检查是否有调用view_exam_details的地方
        if "self.view_exam_details" in content:
            print("✅ view_exam_details方法被正确调用")
        else:
            print("❌ view_exam_details方法未被调用")
            return False
        
        # 检查lambda函数是否正确
        if "lambda e=exam: self.enter_exam_fullscreen(e)" in content:
            print("✅ enter_exam_fullscreen的lambda调用正确")
        else:
            print("❌ enter_exam_fullscreen的lambda调用不正确")
            return False
        
        if "lambda e=exam: self.view_exam_details(e)" in content:
            print("✅ view_exam_details的lambda调用正确")
        else:
            print("❌ view_exam_details的lambda调用不正确")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 方法调用检查失败: {e}")
        return False

def test_no_duplicate_methods():
    """测试是否有重复的方法定义"""
    print("\n🔍 测试4: 重复方法检查")
    print("-" * 40)
    
    try:
        with open("client/client_app.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键方法的出现次数
        methods_to_check = [
            "def view_exam_details",
            "def enter_exam_fullscreen",
            "def enable_anti_cheat_mode"
        ]
        
        for method in methods_to_check:
            count = content.count(method)
            if count == 1:
                print(f"✅ {method} 只定义了一次")
            elif count == 0:
                print(f"❌ {method} 未定义")
                return False
            else:
                print(f"❌ {method} 定义了 {count} 次（重复）")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 重复方法检查失败: {e}")
        return False

def test_client_startup():
    """测试客户端启动"""
    print("\n🔍 测试5: 客户端启动测试")
    print("-" * 40)
    
    try:
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

def main():
    """主测试函数"""
    print("🧪 客户端方法修复验证测试")
    print("=" * 50)
    
    tests = [
        ("语法检查", test_syntax_check),
        ("方法存在性检查", test_method_existence),
        ("方法调用检查", test_method_calls),
        ("重复方法检查", test_no_duplicate_methods),
        ("客户端启动测试", test_client_startup)
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
        print("🎉 所有测试通过！客户端方法修复成功！")
        print("\n✅ 修复内容:")
        print("- 将缺失的方法添加到ExamListView类中")
        print("- 删除了重复的方法定义")
        print("- 修复了AttributeError: 'ExamListView' object has no attribute 'enter_exam_fullscreen'")
        print("- 客户端现在可以正常启动和运行")
        
        print("\n🚀 功能说明:")
        print("- 考生用户：点击'进入考试'按钮会启动全屏防作弊模式")
        print("- 管理员用户：点击'查看详情'按钮会显示考试详情对话框")
        print("- 防作弊功能：禁用快捷键、监控切屏、记录可疑行为")
        
        print("\n🎯 使用方法:")
        print("1. 运行 python main_console.py")
        print("2. 点击'客户机端'按钮")
        print("3. 客户端应该正常启动，状态显示为'运行中'")
        print("4. 登录后可以正常使用考试功能")
    else:
        print("⚠️  部分测试失败，请检查相关问题")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
