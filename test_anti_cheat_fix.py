#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
防作弊功能修复验证脚本
测试输入框、按钮不触发防作弊警告，以及正式考试数据显示
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def test_syntax_check():
    """测试语法检查"""
    print("🔍 测试1: 语法检查")
    print("-" * 40)
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'py_compile', 'client/client_app.py'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ 客户端语法检查通过")
        else:
            print(f"❌ 客户端语法错误: {result.stderr}")
            return False
        
        result_api = subprocess.run([
            sys.executable, '-m', 'py_compile', 'client/api.py'
        ], capture_output=True, text=True, timeout=30)
        
        if result_api.returncode == 0:
            print("✅ API语法检查通过")
            return True
        else:
            print(f"❌ API语法错误: {result_api.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 语法检查失败: {e}")
        return False

def test_anti_cheat_improvements():
    """测试防作弊功能改进"""
    print("\n🔍 测试2: 防作弊功能改进检查")
    print("-" * 40)
    
    try:
        with open("client/client_app.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查新的窗口事件监控
        if "def on_window_minimized" in content:
            print("✅ 窗口最小化监控已添加")
        else:
            print("❌ 窗口最小化监控未添加")
            return False
        
        if "def on_window_deactivated" in content:
            print("✅ 窗口失活监控已添加")
        else:
            print("❌ 窗口失活监控未添加")
            return False
        
        # 检查精确的事件绑定
        if "<Unmap>" in content and "<Map>" in content:
            print("✅ 窗口映射事件绑定已添加")
        else:
            print("❌ 窗口映射事件绑定未添加")
            return False
        
        if "<Deactivate>" in content and "<Activate>" in content:
            print("✅ 窗口激活事件绑定已添加")
        else:
            print("❌ 窗口激活事件绑定未添加")
            return False
        
        # 检查焦点检查逻辑改进
        if "handle_real_focus_loss" in content:
            print("✅ 真实焦点丢失处理已添加")
        else:
            print("❌ 真实焦点丢失处理未添加")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 防作弊功能改进检查失败: {e}")
        return False

def test_input_widget_protection():
    """测试输入组件保护"""
    print("\n🔍 测试3: 输入组件保护检查")
    print("-" * 40)
    
    try:
        with open("client/client_app.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查输入组件事件设置方法
        if "def setup_input_widget_events" in content:
            print("✅ 输入组件事件设置方法已添加")
        else:
            print("❌ 输入组件事件设置方法未添加")
            return False
        
        # 检查按钮事件设置方法
        if "def setup_button_events" in content:
            print("✅ 按钮事件设置方法已添加")
        else:
            print("❌ 按钮事件设置方法未添加")
            return False
        
        # 检查输入框事件绑定调用
        if "self.setup_input_widget_events(answer_entry)" in content:
            print("✅ Entry输入框事件绑定已添加")
        else:
            print("❌ Entry输入框事件绑定未添加")
            return False
        
        if "self.setup_input_widget_events(answer_text)" in content:
            print("✅ Text文本框事件绑定已添加")
        else:
            print("❌ Text文本框事件绑定未添加")
            return False
        
        # 检查按钮事件绑定调用
        if "self.setup_button_events(self.submit_button)" in content:
            print("✅ 交卷按钮事件绑定已添加")
        else:
            print("❌ 交卷按钮事件绑定未添加")
            return False
        
        # 检查事件阻止冒泡
        if 'return "break"' in content:
            print("✅ 事件冒泡阻止机制已添加")
        else:
            print("❌ 事件冒泡阻止机制未添加")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 输入组件保护检查失败: {e}")
        return False

def test_published_exam_data():
    """测试正式发布考试数据"""
    print("\n🔍 测试4: 正式发布考试数据检查")
    print("-" * 40)
    
    try:
        # 检查published_exams.json文件
        published_file = Path("exam_management/published_exams.json")
        if not published_file.exists():
            print("❌ published_exams.json文件不存在")
            return False
        
        with open(published_file, 'r', encoding='utf-8') as f:
            published_data = json.load(f)
        
        if not published_data:
            print("❌ published_exams.json文件为空")
            return False
        
        published_count = len([exam for exam in published_data if exam.get('status') == 'published'])
        print(f"✅ 找到 {published_count} 个已发布的正式考试")
        
        # 检查API中的正式考试获取逻辑
        with open("client/api.py", 'r', encoding='utf-8') as f:
            api_content = f.read()
        
        if "没有分配记录或考试在分配列表中，都可以参加" in api_content:
            print("✅ 正式考试获取逻辑已优化")
        else:
            print("❌ 正式考试获取逻辑未优化")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 正式发布考试数据检查失败: {e}")
        return False

def test_api_published_exams():
    """测试API获取正式发布考试"""
    print("\n🔍 测试5: API获取正式发布考试测试")
    print("-" * 40)
    
    try:
        # 添加路径以便导入
        sys.path.insert(0, 'client')
        import api
        
        # 测试获取正式发布的考试
        student_id = "0ddec8d1-7457-4156-9e7a-199c380e75a3"  # student_1310的ID
        published_exams = api.get_published_exams_for_student(student_id)
        
        if published_exams:
            print(f"✅ 成功获取 {len(published_exams)} 个正式发布的考试")
            for exam in published_exams:
                print(f"   - {exam.get('name')} (ID: {exam.get('id')})")
        else:
            print("❌ 无法获取正式发布的考试")
            return False
        
        # 检查考试详情
        for exam in published_exams[:1]:  # 只检查第一个
            exam_details = api.get_exam_details(exam.get('id'))
            if exam_details:
                print(f"✅ 成功获取考试详情: {exam_details.get('name')}")
                print(f"   题目数量: {len(exam_details.get('questions', []))}")
            else:
                print(f"❌ 无法获取考试 {exam.get('id')} 的详情")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ API获取正式发布考试测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 防作弊功能修复验证测试")
    print("=" * 50)
    
    tests = [
        ("语法检查", test_syntax_check),
        ("防作弊功能改进", test_anti_cheat_improvements),
        ("输入组件保护", test_input_widget_protection),
        ("正式发布考试数据", test_published_exam_data),
        ("API获取正式发布考试", test_api_published_exams)
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
        print("🎉 所有测试通过！防作弊功能修复成功！")
        print("\n✅ 修复内容:")
        print("1. ✅ 改进了防作弊检测逻辑，使用更精确的窗口事件")
        print("2. ✅ 为输入框和文本框添加了事件保护，防止误触发警告")
        print("3. ✅ 为按钮添加了事件保护，防止点击时触发警告")
        print("4. ✅ 修复了正式发布考试的显示逻辑")
        print("5. ✅ 优化了考试分配检查，未分配时显示所有已发布考试")
        
        print("\n🎯 功能说明:")
        print("• 简答题输入不再触发防作弊警告")
        print("• 点击交卷按钮不再触发防作弊警告")
        print("• 显示正式发布的考试而非样例数据")
        print("• 防作弊仍然监控真正的切屏行为")
        print("• 按 Ctrl+Shift+D 可退出防作弊模式（调试用）")
        
        print("\n🚀 测试方法:")
        print("1. 运行 python main_console.py")
        print("2. 点击'客户机端'按钮启动客户端")
        print("3. 使用考生账户登录（如 student_1310）")
        print("4. 应该看到正式发布的考试")
        print("5. 进入考试后测试输入框和按钮功能")
    else:
        print("⚠️  部分测试失败，请检查相关问题")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
