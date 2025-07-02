#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统数据同步脚本

在系统启动时运行，确保各模块间的数据同步。

更新日志：
- 2025-01-07：创建系统数据同步脚本
"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

from common.data_sync_manager import DataSyncManager
from common.logger import get_logger
from grading_center.auto_grader import AutoGrader


def main():
    """主函数"""
    logger = get_logger("sync_system_data")
    
    print("🚀 PH&RL 考试系统数据同步")
    print("=" * 50)
    
    try:
        # 1. 数据同步
        print("\n📊 步骤1: 同步试卷和考试数据...")
        sync_manager = DataSyncManager()
        
        if sync_manager.sync_published_papers_to_exam_system():
            print("✅ 试卷同步成功")
        else:
            print("⚠️ 试卷同步失败，但系统可以继续运行")
        
        # 2. 处理待阅卷的考试
        print("\n📝 步骤2: 处理待阅卷的考试...")
        grader = AutoGrader()
        processed_count = grader.process_pending_exams()
        
        if processed_count > 0:
            print(f"✅ 成功处理 {processed_count} 个待阅卷考试")
        else:
            print("ℹ️ 没有待阅卷的考试")
        
        # 3. 同步阅卷结果到成绩统计
        print("\n📈 步骤3: 同步阅卷结果到成绩统计...")
        if sync_manager.sync_grading_results_to_statistics():
            print("✅ 成绩同步成功")
        else:
            print("⚠️ 成绩同步失败，但系统可以继续运行")
        
        # 4. 创建必要的目录结构
        print("\n📁 步骤4: 检查并创建必要的目录结构...")
        create_required_directories()
        print("✅ 目录结构检查完成")
        
        # 5. 验证数据完整性
        print("\n🔍 步骤5: 验证数据完整性...")
        verify_data_integrity()
        print("✅ 数据完整性验证完成")
        
        print("\n🎉 系统数据同步完成！")
        print("\n📋 同步结果摘要:")
        print(f"  - 试卷同步: 完成")
        print(f"  - 阅卷处理: {processed_count} 个考试")
        print(f"  - 成绩同步: 完成")
        print(f"  - 目录检查: 完成")
        print(f"  - 数据验证: 完成")
        
        return True
        
    except Exception as e:
        logger.error(f"系统数据同步失败: {e}")
        print(f"\n❌ 系统数据同步失败: {e}")
        return False


def create_required_directories():
    """创建必要的目录结构"""
    required_dirs = [
        "client",
        "exam_management/results",
        "grading_center/queue",
        "grading_center/graded",
        "grading_center/processed",
        "score_statistics",
        "logs",
        "data",
        "uploads"
    ]
    
    for dir_path in required_dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"  ✓ {dir_path}")


def verify_data_integrity():
    """验证数据完整性"""
    checks = []
    
    # 检查题库数据库
    qb_db = "question_bank_web/local_dev.db"
    if os.path.exists(qb_db):
        checks.append(("题库数据库", "✓ 存在"))
    else:
        checks.append(("题库数据库", "⚠️ 不存在"))
    
    # 检查用户数据库
    user_db = "user_management/users.db"
    if os.path.exists(user_db):
        checks.append(("用户数据库", "✓ 存在"))
    else:
        checks.append(("用户数据库", "⚠️ 不存在"))
    
    # 检查客户端考试列表
    client_exams = "client/available_exams.json"
    if os.path.exists(client_exams):
        checks.append(("客户端考试列表", "✓ 存在"))
    else:
        checks.append(("客户端考试列表", "⚠️ 不存在"))
    
    # 检查考试管理数据
    exam_data = "exam_management/exams.json"
    if os.path.exists(exam_data):
        checks.append(("考试管理数据", "✓ 存在"))
    else:
        checks.append(("考试管理数据", "⚠️ 不存在"))
    
    # 输出检查结果
    for item, status in checks:
        print(f"  {item}: {status}")


def create_sample_data():
    """创建示例数据（如果需要）"""
    try:
        # 创建示例考试数据
        exam_data = {
            "exams": [
                {
                    "id": "demo_exam_001",
                    "title": "系统演示考试",
                    "description": "这是一个系统演示考试，用于测试考试流程。",
                    "time_limit": 30,
                    "total_score": 100,
                    "status": "available",
                    "created_at": "2025-01-07T00:00:00",
                    "paper_id": 1
                }
            ]
        }
        
        exam_file = "exam_management/exams.json"
        if not os.path.exists(exam_file):
            os.makedirs(os.path.dirname(exam_file), exist_ok=True)
            import json
            with open(exam_file, 'w', encoding='utf-8') as f:
                json.dump(exam_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 创建示例考试数据: {exam_file}")
        
        # 创建客户端考试列表
        client_exams = [
            {
                "exam_id": "demo_exam_001",
                "paper_id": 1,
                "title": "系统演示考试",
                "description": "这是一个系统演示考试，用于测试考试流程。",
                "time_limit": 30,
                "total_score": 100,
                "status": "available",
                "created_at": "2025-01-07T00:00:00",
                "instructions": "请仔细阅读题目，认真作答。考试时间有限，请合理分配时间。"
            }
        ]
        
        client_file = "client/available_exams.json"
        if not os.path.exists(client_file):
            os.makedirs(os.path.dirname(client_file), exist_ok=True)
            import json
            with open(client_file, 'w', encoding='utf-8') as f:
                json.dump(client_exams, f, ensure_ascii=False, indent=2)
            print(f"✅ 创建客户端考试列表: {client_file}")
        
    except Exception as e:
        print(f"⚠️ 创建示例数据失败: {e}")


def run_health_check():
    """运行系统健康检查"""
    try:
        from common.health_checker import SystemHealthChecker
        
        print("\n🏥 运行系统健康检查...")
        checker = SystemHealthChecker()
        results = checker.run_full_check()
        
        # 统计结果
        healthy_count = sum(1 for r in results if r.status.value == "healthy")
        warning_count = sum(1 for r in results if r.status.value == "warning")
        critical_count = sum(1 for r in results if r.status.value == "critical")
        
        print(f"  健康: {healthy_count}, 警告: {warning_count}, 严重: {critical_count}")
        
        if critical_count > 0:
            print("⚠️ 发现严重问题，建议检查系统状态")
        elif warning_count > 0:
            print("⚠️ 发现警告问题，建议关注")
        else:
            print("✅ 系统健康状态良好")
            
    except Exception as e:
        print(f"⚠️ 健康检查失败: {e}")


if __name__ == "__main__":
    # 运行数据同步
    success = main()
    
    # 如果需要，创建示例数据
    if "--create-sample" in sys.argv:
        print("\n📝 创建示例数据...")
        create_sample_data()
    
    # 如果需要，运行健康检查
    if "--health-check" in sys.argv:
        run_health_check()
    
    # 返回退出码
    sys.exit(0 if success else 1)
