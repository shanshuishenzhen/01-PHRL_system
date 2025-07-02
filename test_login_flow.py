#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试登录流程
"""

import sys
sys.path.append('client')
import api

def test_complete_login_flow():
    """测试完整的登录流程"""
    print("=== 测试完整登录流程 ===")
    
    # 1. 测试登录
    print("1. 测试登录...")
    user_info = api.login('student', '123456')
    
    if not user_info:
        print("❌ 登录失败")
        return False
    
    print(f"✅ 登录成功: {user_info.get('username')} (ID: {user_info.get('id')})")
    
    # 2. 测试获取考试列表
    print("2. 测试获取考试列表...")
    exams = api.get_exams_for_student(user_info.get('id'), user_info)
    
    if not exams:
        print("❌ 获取考试列表失败")
        return False
    
    print(f"✅ 获取到 {len(exams)} 个考试")
    
    # 3. 显示考试列表
    print("3. 考试列表:")
    for i, exam in enumerate(exams[:5], 1):  # 只显示前5个
        print(f"   {i}. {exam.get('name')} - {exam.get('status')}")
    
    if len(exams) > 5:
        print(f"   ... 还有 {len(exams) - 5} 个考试")
    
    # 4. 测试获取考试详情
    print("4. 测试获取考试详情...")
    first_exam = exams[0]
    exam_details = api.get_exam_details(first_exam.get('exam_id'))
    
    if not exam_details:
        print("❌ 获取考试详情失败")
        return False
    
    print(f"✅ 获取考试详情成功: {exam_details.get('title')}")
    print(f"   题目数量: {len(exam_details.get('questions', []))}")
    
    return True

def test_user_info_flow():
    """测试用户信息传递流程"""
    print("\n=== 测试用户信息传递流程 ===")
    
    # 模拟客户端应用的流程
    class MockExamApp:
        def __init__(self):
            self.user_info = None
        
        def show_exam_list(self, user_info=None):
            if user_info:
                self.user_info = user_info
                print(f"✅ 设置用户信息: {user_info.get('username')} (ID: {user_info.get('id')})")
            
            if self.user_info and self.user_info.get('id'):
                exams = api.get_exams_for_student(self.user_info['id'], self.user_info)
                print(f"✅ 在ExamListView中获取到 {len(exams)} 个考试")
                return True
            else:
                print("❌ 用户信息无效或缺少ID")
                return False
    
    # 测试流程
    app = MockExamApp()
    
    # 1. 登录
    user_info = api.login('student', '123456')
    if not user_info:
        print("❌ 登录失败")
        return False
    
    # 2. 调用show_exam_list（模拟登录成功后的调用）
    success = app.show_exam_list(user_info)
    
    return success

if __name__ == "__main__":
    print("开始测试...")
    
    # 测试完整登录流程
    flow_success = test_complete_login_flow()
    
    # 测试用户信息传递
    info_success = test_user_info_flow()
    
    print("\n=== 测试结果 ===")
    print(f"完整登录流程: {'✅ 通过' if flow_success else '❌ 失败'}")
    print(f"用户信息传递: {'✅ 通过' if info_success else '❌ 失败'}")
    
    if flow_success and info_success:
        print("\n🎉 所有测试通过！客户端应该能正常显示考试列表了。")
    else:
        print("\n⚠️ 部分测试失败，请检查相关问题。")
