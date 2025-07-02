#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令行版本的考试发布工具

用于快速创建和发布考试，测试完整流程。

更新日志：
- 2025-01-07：创建命令行考试发布工具
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

from exam_management.exam_publisher import ExamPublisher


def create_and_publish_demo_exam():
    """创建并发布一个演示考试"""
    try:
        publisher = ExamPublisher()
        
        print("🚀 开始创建演示考试...")
        
        # 1. 获取可用试卷
        papers = publisher.get_available_papers()
        if not papers:
            print("❌ 没有可用的试卷")
            return False
        
        print(f"📋 找到 {len(papers)} 个可用试卷")
        
        # 选择第一个试卷
        selected_paper = papers[0]
        print(f"📝 选择试卷: {selected_paper['name']}")
        
        # 2. 获取可用学生
        students = publisher.get_available_students()
        if not students:
            print("❌ 没有可用的学生")
            return False
        
        print(f"👥 找到 {len(students)} 个可用学生")
        
        # 选择前3个学生
        selected_students = [s['id'] for s in students[:3]]
        print(f"👤 选择学生: {[s['real_name'] for s in students[:3]]}")
        
        # 3. 创建考试数据
        exam_data = {
            "paper_id": selected_paper['id'],
            "title": f"演示考试 - {selected_paper['name']}",
            "description": f"这是一个基于试卷《{selected_paper['name']}》的演示考试",
            "duration": selected_paper.get('duration', 60),
            "total_score": selected_paper.get('total_score', 100),
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S"),
            "created_by": "demo_admin"
        }
        
        # 4. 创建考试
        print("📝 创建考试...")
        exam_id = publisher.create_exam(exam_data)
        print(f"✅ 考试创建成功，ID: {exam_id}")
        
        # 5. 分配学生
        print("👥 分配学生...")
        success = publisher.assign_students(exam_id, selected_students)
        if success:
            print(f"✅ 成功分配 {len(selected_students)} 个学生")
        else:
            print("❌ 学生分配失败")
            return False
        
        # 6. 发布考试
        print("🚀 发布考试...")
        success = publisher.publish_exam(exam_id)
        if success:
            print("✅ 考试发布成功！")
        else:
            print("❌ 考试发布失败")
            return False
        
        # 7. 验证发布结果
        print("🔍 验证发布结果...")
        published_exams = publisher.get_published_exams()
        published_count = len([e for e in published_exams if e.get('status') == 'published'])
        print(f"📊 当前已发布考试数量: {published_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建演示考试失败: {e}")
        return False


def list_published_exams():
    """列出已发布的考试"""
    try:
        publisher = ExamPublisher()
        
        published_exams = publisher.get_published_exams()
        
        if not published_exams:
            print("📝 没有已发布的考试")
            return
        
        print(f"\n📋 已发布考试列表 ({len(published_exams)}个):")
        print("-" * 80)
        
        for i, exam in enumerate(published_exams, 1):
            enrollments = publisher.get_exam_enrollments(exam['id'])
            student_count = len(enrollments)
            
            print(f"{i}. {exam['title']}")
            print(f"   ID: {exam['id']}")
            print(f"   状态: {exam['status']}")
            print(f"   试卷ID: {exam['paper_id']}")
            print(f"   时长: {exam.get('duration', 60)}分钟")
            print(f"   总分: {exam.get('total_score', 100)}分")
            print(f"   开始时间: {exam.get('start_time', 'N/A')}")
            print(f"   结束时间: {exam.get('end_time', 'N/A')}")
            print(f"   分配学生: {student_count}人")
            print(f"   创建时间: {exam.get('created_at', 'N/A')}")
            print("-" * 80)
        
    except Exception as e:
        print(f"❌ 获取考试列表失败: {e}")


def trigger_data_sync():
    """触发数据同步"""
    try:
        print("🔄 触发数据同步...")
        
        from common.data_sync_manager import DataSyncManager
        sync_manager = DataSyncManager()
        
        # 同步已发布考试到客户端
        success = sync_manager.sync_published_exams_to_client()
        
        if success:
            print("✅ 数据同步成功")
        else:
            print("❌ 数据同步失败")
        
        return success
        
    except Exception as e:
        print(f"❌ 数据同步失败: {e}")
        return False


def main():
    """主函数"""
    print("🎯 PH&RL 考试发布工具")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("1. 创建并发布演示考试")
        print("2. 列出已发布考试")
        print("3. 触发数据同步")
        print("4. 查看系统状态")
        print("0. 退出")
        
        choice = input("\n请输入选择 (0-4): ").strip()
        
        if choice == "1":
            success = create_and_publish_demo_exam()
            if success:
                print("\n🎉 演示考试创建并发布成功！")
                print("💡 提示: 现在可以在客户端登录查看考试")
            else:
                print("\n❌ 演示考试创建失败")
        
        elif choice == "2":
            list_published_exams()
        
        elif choice == "3":
            trigger_data_sync()
        
        elif choice == "4":
            publisher = ExamPublisher()
            papers = publisher.get_available_papers()
            students = publisher.get_available_students()
            published_exams = publisher.get_published_exams()
            
            print(f"\n📊 系统状态:")
            print(f"  可用试卷: {len(papers)}个")
            print(f"  可用学生: {len(students)}个")
            print(f"  已发布考试: {len(published_exams)}个")
        
        elif choice == "0":
            print("👋 再见！")
            break
        
        else:
            print("❌ 无效选择，请重新输入")


if __name__ == "__main__":
    main()
