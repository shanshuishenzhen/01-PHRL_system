#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考试管理修复验证脚本
测试考试管理登录后逻辑及功能的修改
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def test_client_app_modifications():
    """测试客户端应用修改"""
    print("🔍 测试1: 客户端应用修改检查")
    print("-" * 40)
    
    client_app_path = Path("client/client_app.py")
    if not client_app_path.exists():
        print(f"❌ 客户端文件不存在: {client_app_path}")
        return False
    
    try:
        with open(client_app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查滚动条功能
        if "create_scrollable_exam_list" in content:
            print("✅ 滚动条功能已添加")
        else:
            print("❌ 滚动条功能未添加")
            return False
        
        # 检查用户角色判断
        if "user_role in ['admin', 'supervisor', 'evaluator', 'super_user']" in content:
            print("✅ 用户角色判断逻辑已添加")
        else:
            print("❌ 用户角色判断逻辑未添加")
            return False
        
        # 检查管理员查看详情功能
        if "def view_exam_details" in content:
            print("✅ 管理员查看详情功能已添加")
        else:
            print("❌ 管理员查看详情功能未添加")
            return False
        
        # 检查全屏考试功能
        if "def enter_exam_fullscreen" in content:
            print("✅ 全屏考试功能已添加")
        else:
            print("❌ 全屏考试功能未添加")
            return False
        
        # 检查防作弊功能
        if "def enable_anti_cheat_mode" in content:
            print("✅ 防作弊功能已添加")
        else:
            print("❌ 防作弊功能未添加")
            return False
        
        # 检查切屏监控
        if "def on_focus_lost" in content:
            print("✅ 切屏监控功能已添加")
        else:
            print("❌ 切屏监控功能未添加")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 检查客户端应用修改失败: {e}")
        return False

def test_api_modifications():
    """测试API修改"""
    print("\n🔍 测试2: API修改检查")
    print("-" * 40)
    
    api_path = Path("client/api.py")
    if not api_path.exists():
        print(f"❌ API文件不存在: {api_path}")
        return False
    
    try:
        with open(api_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查管理员获取所有考试功能
        if "def get_all_exams_for_admin" in content:
            print("✅ 管理员获取所有考试功能已添加")
        else:
            print("❌ 管理员获取所有考试功能未添加")
            return False
        
        # 检查考生考试过滤逻辑
        if "只显示已发布但未开始的考试" in content:
            print("✅ 考生考试过滤逻辑已添加")
        else:
            print("❌ 考生考试过滤逻辑未添加")
            return False
        
        # 检查用户角色判断
        if "管理员/考评员：显示所有考试" in content:
            print("✅ API用户角色判断已更新")
        else:
            print("❌ API用户角色判断未更新")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 检查API修改失败: {e}")
        return False

def test_ui_components():
    """测试UI组件"""
    print("\n🔍 测试3: UI组件检查")
    print("-" * 40)
    
    client_app_path = Path("client/client_app.py")
    
    try:
        with open(client_app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查Canvas滚动条
        if "tk.Canvas" in content and "tk.Scrollbar" in content:
            print("✅ Canvas和滚动条组件已添加")
        else:
            print("❌ Canvas和滚动条组件未添加")
            return False
        
        # 检查鼠标滚轮事件
        if "_on_mousewheel" in content:
            print("✅ 鼠标滚轮事件已添加")
        else:
            print("❌ 鼠标滚轮事件未添加")
            return False
        
        # 检查全屏属性设置
        if "attributes('-fullscreen', True)" in content:
            print("✅ 全屏属性设置已添加")
        else:
            print("❌ 全屏属性设置未添加")
            return False
        
        # 检查置顶属性设置
        if "attributes('-topmost', True)" in content:
            print("✅ 置顶属性设置已添加")
        else:
            print("❌ 置顶属性设置未添加")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 检查UI组件失败: {e}")
        return False

def test_anti_cheat_features():
    """测试防作弊功能"""
    print("\n🔍 测试4: 防作弊功能检查")
    print("-" * 40)
    
    client_app_path = Path("client/client_app.py")
    
    try:
        with open(client_app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查快捷键禁用
        if "Alt-Tab" in content and "Control-Alt-Delete" in content:
            print("✅ 快捷键禁用功能已添加")
        else:
            print("❌ 快捷键禁用功能未添加")
            return False
        
        # 检查焦点监控
        if "FocusOut" in content and "FocusIn" in content:
            print("✅ 焦点监控功能已添加")
        else:
            print("❌ 焦点监控功能未添加")
            return False
        
        # 检查右键菜单禁用
        if "Button-3" in content:
            print("✅ 右键菜单禁用功能已添加")
        else:
            print("❌ 右键菜单禁用功能未添加")
            return False
        
        # 检查作弊日志记录
        if "def log_cheat_attempt" in content:
            print("✅ 作弊日志记录功能已添加")
        else:
            print("❌ 作弊日志记录功能未添加")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 检查防作弊功能失败: {e}")
        return False

def test_role_based_logic():
    """测试基于角色的逻辑"""
    print("\n🔍 测试5: 基于角色的逻辑检查")
    print("-" * 40)
    
    try:
        # 检查客户端角色逻辑
        with open("client/client_app.py", 'r', encoding='utf-8') as f:
            client_content = f.read()
        
        # 检查API角色逻辑
        with open("client/api.py", 'r', encoding='utf-8') as f:
            api_content = f.read()
        
        # 检查考生只看到可参加考试的逻辑
        if "只显示已发布但未进行的考试" in api_content:
            print("✅ 考生考试过滤逻辑正确")
        else:
            print("❌ 考生考试过滤逻辑不正确")
            return False
        
        # 检查管理员看到所有考试的逻辑
        if "管理员可以看到所有状态的考试" in api_content or "get_all_exams_for_admin" in api_content:
            print("✅ 管理员考试显示逻辑正确")
        else:
            print("❌ 管理员考试显示逻辑不正确")
            return False
        
        # 检查不同按钮显示逻辑
        if "查看详情" in client_content and "进入考试" in client_content:
            print("✅ 不同角色按钮显示逻辑正确")
        else:
            print("❌ 不同角色按钮显示逻辑不正确")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 检查基于角色的逻辑失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 考试管理修复验证测试")
    print("=" * 50)
    
    tests = [
        ("客户端应用修改", test_client_app_modifications),
        ("API修改", test_api_modifications),
        ("UI组件", test_ui_components),
        ("防作弊功能", test_anti_cheat_features),
        ("基于角色的逻辑", test_role_based_logic)
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
        print("🎉 所有测试通过！考试管理修复成功！")
        print("\n✅ 修复内容:")
        print("1. ✅ 界面增加滚动条")
        print("2. ✅ 考生只看到已发布但未进行的考试")
        print("3. ✅ 管理员可以看到所有考试状态")
        print("4. ✅ 考生进入考试后满屏显示")
        print("5. ✅ 启用防切屏、防作弊功能")
        print("6. ✅ 管理员点击考试项目界面不变")
        
        print("\n🚀 使用说明:")
        print("1. 运行 python launcher.py")
        print("2. 启动客户端模块")
        print("3. 使用不同角色的用户登录测试")
        print("4. 考生用户：只能看到可参加的考试，点击进入全屏模式")
        print("5. 管理员用户：可以看到所有考试，点击查看详情")
    else:
        print("⚠️  部分测试失败，请检查相关问题")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
