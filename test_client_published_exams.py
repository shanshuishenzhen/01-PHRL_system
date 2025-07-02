#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试客户端是否正确显示已发布考试

验证客户端登录后显示的是考试管理模块发布的考试，而不是样例考试。

更新日志：
- 2025-01-07：创建客户端已发布考试测试
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))
sys.path.append('client')

import api


def test_api_returns_published_exams():
    """测试API是否返回已发布考试"""
    print("🧪 测试API返回已发布考试...")
    
    try:
        student_id = '1640ffbe-5661-49a3-b2e3-7c24215e828c'
        user_info = {'username': 'student', 'id': student_id}
        
        # 获取考试列表
        exams = api.get_exams_for_student(student_id, user_info)
        
        if not exams:
            print("❌ API没有返回任何考试")
            return False
        
        # 检查考试类型
        published_count = 0
        sample_count = 0
        
        for exam in exams:
            exam_type = exam.get('exam_type', '未知')
            exam_name = exam.get('name', '未知')
            
            if exam_type == 'published':
                published_count += 1
                print(f"✅ 已发布考试: {exam_name}")
            elif '示例' in exam_name or '样例' in exam_name or 'sample' in exam_name.lower():
                sample_count += 1
                print(f"⚠️ 样例考试: {exam_name}")
            else:
                print(f"❓ 未知类型考试: {exam_name} (类型: {exam_type})")
        
        print(f"📊 统计: 已发布考试 {published_count} 个, 样例考试 {sample_count} 个")
        
        if published_count > 0 and sample_count == 0:
            print("✅ API正确返回已发布考试，没有样例考试")
            return True
        elif published_count > 0 and sample_count > 0:
            print("⚠️ API返回了已发布考试，但也包含样例考试")
            return False
        else:
            print("❌ API没有返回已发布考试")
            return False
            
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False


def test_published_exams_vs_sample_exams():
    """对比已发布考试和样例考试"""
    print("\n🧪 对比已发布考试和样例考试...")
    
    try:
        student_id = '1640ffbe-5661-49a3-b2e3-7c24215e828c'
        
        # 1. 测试已发布考试API
        published_exams = api.get_published_exams_for_student(student_id)
        print(f"📋 已发布考试API返回: {len(published_exams)} 个考试")
        
        for exam in published_exams:
            print(f"  - {exam.get('name')} (ID: {exam.get('id')})")
        
        # 2. 测试完整API
        user_info = {'username': 'student', 'id': student_id}
        all_exams = api.get_exams_for_student(student_id, user_info)
        print(f"📋 完整API返回: {len(all_exams)} 个考试")
        
        for exam in all_exams:
            exam_type = exam.get('exam_type', '未知')
            print(f"  - {exam.get('name')} (类型: {exam_type})")
        
        # 3. 验证一致性
        if len(published_exams) == len(all_exams):
            print("✅ 已发布考试API和完整API返回的考试数量一致")
            return True
        else:
            print("❌ 已发布考试API和完整API返回的考试数量不一致")
            return False
            
    except Exception as e:
        print(f"❌ 对比测试失败: {e}")
        return False


def test_exam_details():
    """测试考试详情"""
    print("\n🧪 测试考试详情...")
    
    try:
        student_id = '1640ffbe-5661-49a3-b2e3-7c24215e828c'
        user_info = {'username': 'student', 'id': student_id}
        
        # 获取考试列表
        exams = api.get_exams_for_student(student_id, user_info)
        
        if not exams:
            print("❌ 没有考试可测试")
            return False
        
        # 测试第一个考试的详情
        first_exam = exams[0]
        exam_id = first_exam.get('id')
        
        print(f"📝 测试考试详情: {first_exam.get('name')}")
        
        # 获取考试详情
        exam_details = api.get_exam_details(exam_id)
        
        if exam_details:
            print(f"✅ 考试详情获取成功")
            print(f"  - 标题: {exam_details.get('title', exam_details.get('name'))}")
            print(f"  - 题目数量: {len(exam_details.get('questions', []))}")
            print(f"  - 总分: {exam_details.get('total_score')}")
            print(f"  - 时长: {exam_details.get('duration')}分钟")
            
            # 检查是否是真实题目还是样例题目
            questions = exam_details.get('questions', [])
            if questions:
                first_question = questions[0]
                question_content = first_question.get('content', '')
                
                if '示例' in question_content or 'sample' in question_content.lower():
                    print("⚠️ 考试包含样例题目")
                    return False
                else:
                    print("✅ 考试包含真实题目")
                    return True
            else:
                print("❌ 考试没有题目")
                return False
        else:
            print("❌ 考试详情获取失败")
            return False
            
    except Exception as e:
        print(f"❌ 考试详情测试失败: {e}")
        return False


def test_client_login_flow():
    """测试客户端登录流程"""
    print("\n🧪 测试客户端登录流程...")
    
    try:
        # 模拟登录流程
        username = 'student'
        password = '123456'
        
        print(f"🔐 模拟登录: {username}")
        
        # 1. 登录
        user_info = api.login(username, password)
        if not user_info:
            print("❌ 登录失败")
            return False
        
        print(f"✅ 登录成功: {user_info.get('real_name', user_info.get('username'))}")
        
        # 2. 获取考试列表
        student_id = user_info.get('id')
        exams = api.get_exams_for_student(student_id, user_info)
        
        if not exams:
            print("❌ 登录后没有获取到考试")
            return False
        
        print(f"✅ 获取到 {len(exams)} 个考试")
        
        # 3. 检查考试类型
        for exam in exams:
            exam_type = exam.get('exam_type', '未知')
            if exam_type == 'published':
                print(f"✅ 已发布考试: {exam.get('name')}")
            else:
                print(f"⚠️ 非已发布考试: {exam.get('name')} (类型: {exam_type})")
        
        return True
        
    except Exception as e:
        print(f"❌ 客户端登录流程测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🎯 客户端已发布考试测试")
    print("=" * 50)
    
    tests = [
        ("API返回已发布考试", test_api_returns_published_exams),
        ("已发布考试vs样例考试", test_published_exams_vs_sample_exams),
        ("考试详情", test_exam_details),
        ("客户端登录流程", test_client_login_flow)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！客户端正确显示已发布考试。")
        print("\n💡 现在客户端登录后将显示:")
        print("✅ 考试管理模块发布的真实考试")
        print("❌ 不再显示自动生成的样例考试")
    else:
        print("⚠️ 部分测试失败，客户端可能仍在显示样例考试。")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
