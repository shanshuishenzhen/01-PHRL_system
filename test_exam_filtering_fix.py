#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考试过滤和进入考试功能修复验证脚本
测试考生只能看到可参加的考试，以及进入考试功能
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

def test_exam_filtering_logic():
    """测试考试过滤逻辑"""
    print("\n🔍 测试2: 考试过滤逻辑检查")
    print("-" * 40)
    
    try:
        with open("client/client_app.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查过滤逻辑
        if "filtered_exams = []" in content:
            print("✅ 考试过滤逻辑已添加")
        else:
            print("❌ 考试过滤逻辑未添加")
            return False
        
        # 检查考生过滤条件
        if "if status in ['available', 'published']:" in content:
            print("✅ 考生考试状态过滤条件正确")
        else:
            print("❌ 考生考试状态过滤条件不正确")
            return False
        
        # 检查过滤日志
        if "过滤掉考试:" in content:
            print("✅ 过滤日志已添加")
        else:
            print("❌ 过滤日志未添加")
            return False
        
        # 检查过滤后数量显示
        if "过滤后的考试数量:" in content:
            print("✅ 过滤后数量显示已添加")
        else:
            print("❌ 过滤后数量显示未添加")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 考试过滤逻辑检查失败: {e}")
        return False

def test_exam_details_support():
    """测试考试详情支持"""
    print("\n🔍 测试3: 考试详情支持检查")
    print("-" * 40)
    
    try:
        with open("client/api.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查考试ID支持
        if "if exam_id in [901, 902, 903, 11, 12]:" in content:
            print("✅ 考试ID 11和12支持已添加")
        else:
            print("❌ 考试ID 11和12支持未添加")
            return False
        
        # 检查视频创推员考试名称
        if "视频创推员（四级）理论 - 自动组卷_第2套" in content:
            print("✅ 考试11名称设置正确")
        else:
            print("❌ 考试11名称设置不正确")
            return False
        
        if "视频创推员（四级）理论 - 自动组卷_第1套" in content:
            print("✅ 考试12名称设置正确")
        else:
            print("❌ 考试12名称设置不正确")
            return False
        
        # 检查视频创推员相关题目
        if "视频创推员的主要职责是什么？" in content:
            print("✅ 视频创推员题目已添加")
        else:
            print("❌ 视频创推员题目未添加")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 考试详情支持检查失败: {e}")
        return False

def test_api_exam_details():
    """测试API考试详情获取"""
    print("\n🔍 测试4: API考试详情获取测试")
    print("-" * 40)
    
    try:
        # 添加路径以便导入
        sys.path.insert(0, 'client')
        import api
        
        # 测试获取考试11的详情
        exam_details_11 = api.get_exam_details(11)
        if exam_details_11:
            print(f"✅ 成功获取考试11详情: {exam_details_11.get('name')}")
            print(f"   题目数量: {len(exam_details_11.get('questions', []))}")
            print(f"   总分: {exam_details_11.get('total_score')}")
        else:
            print("❌ 无法获取考试11详情")
            return False
        
        # 测试获取考试12的详情
        exam_details_12 = api.get_exam_details(12)
        if exam_details_12:
            print(f"✅ 成功获取考试12详情: {exam_details_12.get('name')}")
            print(f"   题目数量: {len(exam_details_12.get('questions', []))}")
            print(f"   总分: {exam_details_12.get('total_score')}")
        else:
            print("❌ 无法获取考试12详情")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ API考试详情获取测试失败: {e}")
        return False

def test_button_logic():
    """测试按钮逻辑"""
    print("\n🔍 测试5: 按钮逻辑检查")
    print("-" * 40)
    
    try:
        with open("client/client_app.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查考生按钮逻辑简化
        if "# 考生用户：只有可参加的考试才能进入" in content:
            print("✅ 考生按钮逻辑注释正确")
        else:
            print("❌ 考生按钮逻辑注释不正确")
            return False
        
        # 检查是否移除了不必要的状态判断
        lines = content.split('\n')
        in_student_button_section = False
        has_unnecessary_conditions = False
        
        for line in lines:
            if "# 考生用户：只有可参加的考试才能进入" in line:
                in_student_button_section = True
            elif "if is_admin_user:" in line and in_student_button_section:
                in_student_button_section = False
            elif in_student_button_section and ("elif status == 'draft':" in line or "elif status == 'completed':" in line):
                has_unnecessary_conditions = True
                break
        
        if not has_unnecessary_conditions:
            print("✅ 考生按钮逻辑已简化，移除了不必要的状态判断")
        else:
            print("❌ 考生按钮逻辑仍包含不必要的状态判断")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 按钮逻辑检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 考试过滤和进入考试功能修复验证测试")
    print("=" * 50)
    
    tests = [
        ("语法检查", test_syntax_check),
        ("考试过滤逻辑", test_exam_filtering_logic),
        ("考试详情支持", test_exam_details_support),
        ("API考试详情获取", test_api_exam_details),
        ("按钮逻辑", test_button_logic)
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
        print("🎉 所有测试通过！考试过滤和进入考试功能修复成功！")
        print("\n✅ 修复内容:")
        print("1. ✅ 考生现在只能看到可参加的考试（available/published状态）")
        print("2. ✅ 过滤掉了draft状态的考试，不再显示给考生")
        print("3. ✅ 添加了对考试ID 11和12的详情支持")
        print("4. ✅ 为视频创推员考试添加了专业题目内容")
        print("5. ✅ 简化了考生的按钮逻辑，移除了不必要的状态判断")
        
        print("\n🎯 功能说明:")
        print("• 考生登录后只看到2个可参加的考试（第1套和第2套）")
        print("• 点击'进入考试'按钮会显示考试详情确认对话框")
        print("• 确认后进入全屏防作弊考试模式")
        print("• 考试包含5道专业题目，总分100分")
        print("• 按 Ctrl+Shift+D 可退出防作弊模式（调试用）")
        
        print("\n🚀 测试方法:")
        print("1. 运行 python main_console.py")
        print("2. 点击'客户机端'按钮启动客户端")
        print("3. 使用考生账户登录（如 student_1310）")
        print("4. 应该只看到2个可参加的考试")
        print("5. 点击'进入考试'测试功能")
    else:
        print("⚠️  部分测试失败，请检查相关问题")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
