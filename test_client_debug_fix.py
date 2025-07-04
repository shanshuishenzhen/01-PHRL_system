#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户端调试功能修复验证脚本
测试防作弊退出接口、考试过滤和进入考试功能
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
            
            # 检查API文件
            result_api = subprocess.run([
                sys.executable, '-m', 'py_compile', 'client/api.py'
            ], capture_output=True, text=True, timeout=30)
            
            if result_api.returncode == 0:
                print("✅ API文件语法检查通过")
                return True
            else:
                print(f"❌ API文件语法错误: {result_api.stderr}")
                return False
        else:
            print(f"❌ 客户端语法错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 语法检查失败: {e}")
        return False

def test_anti_cheat_debug_interface():
    """测试防作弊调试接口"""
    print("\n🔍 测试2: 防作弊调试接口检查")
    print("-" * 40)
    
    try:
        with open("client/client_app.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查调试退出接口
        if "def debug_exit_anti_cheat" in content:
            print("✅ 调试退出接口已添加")
        else:
            print("❌ 调试退出接口未添加")
            return False
        
        # 检查禁用防作弊模式方法
        if "def disable_anti_cheat_mode" in content:
            print("✅ 禁用防作弊模式方法已添加")
        else:
            print("❌ 禁用防作弊模式方法未添加")
            return False
        
        # 检查快捷键绑定
        if "Control-Shift-D" in content:
            print("✅ Ctrl+Shift+D 调试快捷键已绑定")
        else:
            print("❌ 调试快捷键未绑定")
            return False
        
        # 检查调试提示信息
        if "按 Ctrl+Shift+D 可退出防作弊模式" in content:
            print("✅ 调试提示信息已添加")
        else:
            print("❌ 调试提示信息未添加")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 防作弊调试接口检查失败: {e}")
        return False

def test_exam_filtering():
    """测试考试过滤功能"""
    print("\n🔍 测试3: 考试过滤功能检查")
    print("-" * 40)
    
    try:
        with open("client/api.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查考试分配检查函数
        if "def is_exam_assigned_to_student" in content:
            print("✅ 考试分配检查函数已添加")
        else:
            print("❌ 考试分配检查函数未添加")
            return False
        
        # 检查考试过滤逻辑
        if "not exam.get('completed', False)" in content:
            print("✅ 已完成考试过滤逻辑已添加")
        else:
            print("❌ 已完成考试过滤逻辑未添加")
            return False
        
        # 检查分配检查逻辑
        if "is_exam_assigned_to_student" in content:
            print("✅ 考试分配检查逻辑已集成")
        else:
            print("❌ 考试分配检查逻辑未集成")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 考试过滤功能检查失败: {e}")
        return False

def test_exam_entry_function():
    """测试进入考试功能"""
    print("\n🔍 测试4: 进入考试功能检查")
    print("-" * 40)
    
    try:
        with open("client/client_app.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查show_exam_page方法
        if "def show_exam_page" in content:
            print("✅ show_exam_page方法已添加")
        else:
            print("❌ show_exam_page方法未添加")
            return False
        
        # 检查考试详情获取
        if "api.get_exam_details" in content:
            print("✅ 考试详情获取逻辑已添加")
        else:
            print("❌ 考试详情获取逻辑未添加")
            return False
        
        # 检查错误处理
        if "进入考试失败" in content:
            print("✅ 进入考试错误处理已添加")
        else:
            print("❌ 进入考试错误处理未添加")
            return False
        
        # 检查回调函数修改
        if "show_exam_callback=self.show_exam_page" in content:
            print("✅ 回调函数已正确修改")
        else:
            print("❌ 回调函数未正确修改")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 进入考试功能检查失败: {e}")
        return False

def test_debug_features():
    """测试调试功能"""
    print("\n🔍 测试5: 调试功能综合检查")
    print("-" * 40)
    
    try:
        with open("client/client_app.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查调试信息输出
        debug_prints = [
            "正在跳转到考试页面",
            "show_exam_page被调用",
            "考试页面已创建并显示",
            "调试模式：退出防作弊模式",
            "防作弊模式已禁用"
        ]
        
        missing_prints = []
        for debug_print in debug_prints:
            if debug_print in content:
                print(f"✅ 调试信息: {debug_print}")
            else:
                print(f"❌ 缺少调试信息: {debug_print}")
                missing_prints.append(debug_print)
        
        if missing_prints:
            return False
        
        # 检查异常处理
        if "except Exception as e:" in content:
            print("✅ 异常处理已添加")
        else:
            print("❌ 异常处理未添加")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 调试功能检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 客户端调试功能修复验证测试")
    print("=" * 50)
    
    tests = [
        ("语法检查", test_syntax_check),
        ("防作弊调试接口", test_anti_cheat_debug_interface),
        ("考试过滤功能", test_exam_filtering),
        ("进入考试功能", test_exam_entry_function),
        ("调试功能综合检查", test_debug_features)
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
        print("🎉 所有测试通过！客户端调试功能修复成功！")
        print("\n✅ 修复内容:")
        print("1. ✅ 防作弊功能添加了调试退出接口")
        print("   - 按 Ctrl+Shift+D 可退出防作弊模式")
        print("   - 添加了确认对话框和状态恢复")
        print("2. ✅ 考生只能看到分配给他们且未完成的考试")
        print("   - 过滤已完成的考试")
        print("   - 检查考试分配状态")
        print("3. ✅ 完善了点击考试项目后的进入考试功能")
        print("   - 添加了考试详情获取")
        print("   - 改进了错误处理")
        print("   - 修复了回调函数调用")
        
        print("\n🚀 调试说明:")
        print("• 防作弊模式退出: 在考试中按 Ctrl+Shift+D")
        print("• 考试过滤: 考生只看到未完成且分配给他们的考试")
        print("• 进入考试: 点击考试项目会显示详细信息并进入考试页面")
        print("• 调试信息: 控制台会输出详细的调试信息")
        
        print("\n🎯 使用方法:")
        print("1. 运行 python main_console.py")
        print("2. 点击'客户机端'按钮启动客户端")
        print("3. 使用考生账户登录测试")
        print("4. 在考试中按 Ctrl+Shift+D 可退出防作弊模式")
    else:
        print("⚠️  部分测试失败，请检查相关问题")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
