#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考试管理集成测试

验证考试发布管理器与考试管理模块的集成是否正常工作。

更新日志：
- 2025-01-07：创建集成测试脚本
"""

import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from exam_management.exam_publisher import ExamPublisher


def test_exam_publisher():
    """测试考试发布管理器"""
    print("🧪 测试考试发布管理器...")
    
    try:
        publisher = ExamPublisher()
        
        # 1. 测试获取试卷
        papers = publisher.get_available_papers()
        print(f"✅ 获取试卷: {len(papers)}个")
        
        # 2. 测试获取学生
        students = publisher.get_available_students()
        print(f"✅ 获取学生: {len(students)}个")
        
        # 3. 测试获取已发布考试
        published_exams = publisher.get_published_exams()
        print(f"✅ 已发布考试: {len(published_exams)}个")
        
        return True
        
    except Exception as e:
        print(f"❌ 考试发布管理器测试失败: {e}")
        return False


def test_enrollments_format():
    """测试enrollments.json格式兼容性"""
    print("\n🧪 测试enrollments.json格式...")
    
    try:
        enrollments_file = Path("exam_management/enrollments.json")
        
        if not enrollments_file.exists():
            print("❌ enrollments.json文件不存在")
            return False
        
        with open(enrollments_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查格式
        if not isinstance(data, dict):
            print("❌ enrollments.json应该是字典格式")
            return False
        
        if "enrollments" not in data:
            print("❌ enrollments.json缺少'enrollments'键")
            return False
        
        enrollments = data["enrollments"]
        if not isinstance(enrollments, list):
            print("❌ enrollments应该是列表格式")
            return False
        
        # 检查每个enrollment记录
        for i, enrollment in enumerate(enrollments):
            if not isinstance(enrollment, dict):
                print(f"❌ enrollment[{i}]应该是字典格式")
                return False
            
            required_keys = ["exam_id", "user_ids"]
            for key in required_keys:
                if key not in enrollment:
                    print(f"❌ enrollment[{i}]缺少'{key}'键")
                    return False
            
            if not isinstance(enrollment["user_ids"], list):
                print(f"❌ enrollment[{i}]['user_ids']应该是列表格式")
                return False
        
        print(f"✅ enrollments.json格式正确，包含{len(enrollments)}个考试分配")
        return True
        
    except Exception as e:
        print(f"❌ enrollments.json格式测试失败: {e}")
        return False


def test_published_exams_format():
    """测试published_exams.json格式"""
    print("\n🧪 测试published_exams.json格式...")
    
    try:
        published_exams_file = Path("exam_management/published_exams.json")
        
        if not published_exams_file.exists():
            print("❌ published_exams.json文件不存在")
            return False
        
        with open(published_exams_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("❌ published_exams.json应该是列表格式")
            return False
        
        published_count = 0
        for i, exam in enumerate(data):
            if not isinstance(exam, dict):
                print(f"❌ exam[{i}]应该是字典格式")
                return False
            
            required_keys = ["id", "title", "status", "paper_id"]
            for key in required_keys:
                if key not in exam:
                    print(f"❌ exam[{i}]缺少'{key}'键")
                    return False
            
            if exam["status"] == "published":
                published_count += 1
        
        print(f"✅ published_exams.json格式正确，包含{len(data)}个考试，其中{published_count}个已发布")
        return True
        
    except Exception as e:
        print(f"❌ published_exams.json格式测试失败: {e}")
        return False


def test_client_exams_sync():
    """测试客户端考试同步"""
    print("\n🧪 测试客户端考试同步...")
    
    try:
        client_exams_file = Path("client/available_exams.json")
        
        if not client_exams_file.exists():
            print("❌ client/available_exams.json文件不存在")
            return False
        
        with open(client_exams_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("❌ available_exams.json应该是列表格式")
            return False
        
        available_count = 0
        for i, exam in enumerate(data):
            if not isinstance(exam, dict):
                print(f"❌ client_exam[{i}]应该是字典格式")
                return False
            
            required_keys = ["exam_id", "name", "status"]
            for key in required_keys:
                if key not in exam:
                    print(f"❌ client_exam[{i}]缺少'{key}'键")
                    return False
            
            if exam["status"] == "available":
                available_count += 1
        
        print(f"✅ 客户端考试同步正常，包含{len(data)}个考试，其中{available_count}个可用")
        return True
        
    except Exception as e:
        print(f"❌ 客户端考试同步测试失败: {e}")
        return False


def test_student_assignment():
    """测试学生分配"""
    print("\n🧪 测试学生分配...")
    
    try:
        # 测试特定学生是否被分配到考试
        test_student_id = "1640ffbe-5661-49a3-b2e3-7c24215e828c"  # student用户
        
        with open("exam_management/enrollments.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assigned_exams = []
        for enrollment in data["enrollments"]:
            if test_student_id in enrollment["user_ids"]:
                assigned_exams.append(enrollment["exam_id"])
        
        if assigned_exams:
            print(f"✅ 测试学生已分配到{len(assigned_exams)}个考试")
            return True
        else:
            print("❌ 测试学生未分配到任何考试")
            return False
        
    except Exception as e:
        print(f"❌ 学生分配测试失败: {e}")
        return False


def test_api_integration():
    """测试API集成"""
    print("\n🧪 测试API集成...")
    
    try:
        sys.path.append('client')
        import api
        
        # 测试获取已发布考试
        test_student_id = "1640ffbe-5661-49a3-b2e3-7c24215e828c"
        published_exams = api.get_published_exams_for_student(test_student_id)
        
        print(f"✅ API获取已发布考试: {len(published_exams)}个")
        
        # 测试完整的考试获取流程
        user_info = {"username": "student", "id": test_student_id}
        all_exams = api.get_exams_for_student(test_student_id, user_info)
        
        print(f"✅ API获取所有考试: {len(all_exams)}个")
        
        return len(published_exams) > 0 or len(all_exams) > 0
        
    except Exception as e:
        print(f"❌ API集成测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🎯 考试管理集成测试")
    print("=" * 50)
    
    tests = [
        ("考试发布管理器", test_exam_publisher),
        ("enrollments.json格式", test_enrollments_format),
        ("published_exams.json格式", test_published_exams_format),
        ("客户端考试同步", test_client_exams_sync),
        ("学生分配", test_student_assignment),
        ("API集成", test_api_integration)
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
        print("🎉 所有测试通过！考试管理集成正常工作。")
        print("\n💡 现在可以：")
        print("1. 启动考试管理模块: python exam_management/simple_exam_manager.py")
        print("2. 启动客户端: python client/client_app.py")
        print("3. 使用考试发布工具: python exam_management/publish_exam_cli.py")
    else:
        print("⚠️ 部分测试失败，请检查相关问题。")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
