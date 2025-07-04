#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PH&RL 在线考试系统 - 全流程自动化测试脚本
基于 COMPLETE_EXAM_FLOW_TEST.md 的测试流程
"""

import os
import sys
import json
import sqlite3
import time
import subprocess
from datetime import datetime
from pathlib import Path

class FullFlowTester:
    def __init__(self):
        self.test_results = {
            "start_time": datetime.now().isoformat(),
            "tests": {},
            "overall_status": "RUNNING"
        }
        
    def log(self, message, level="INFO"):
        """记录测试日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_environment_setup(self):
        """测试1: 环境设置检查"""
        self.log("🔧 测试1: 环境设置检查")
        
        checks = {
            "python_venv": os.path.exists("venv"),
            "question_db": os.path.exists("question_bank_web/local_dev.db"),
            "user_data": os.path.exists("user_management/users.json"),
            "client_exams": os.path.exists("client/available_exams.json"),
            "exam_management": os.path.exists("exam_management/published_exams.json")
        }
        
        all_passed = True
        for check, result in checks.items():
            status = "✅" if result else "❌"
            self.log(f"  {status} {check}: {'通过' if result else '失败'}")
            if not result:
                all_passed = False
                
        self.test_results["tests"]["environment_setup"] = {
            "status": "PASS" if all_passed else "FAIL",
            "details": checks
        }
        
        return all_passed
    
    def test_database_content(self):
        """测试2: 数据库内容验证"""
        self.log("🗄️ 测试2: 数据库内容验证")
        
        try:
            # 检查题库数据库
            conn = sqlite3.connect("question_bank_web/local_dev.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM papers")
            paper_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM questions")
            question_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM paper_questions")
            paper_question_count = cursor.fetchone()[0]
            
            conn.close()
            
            self.log(f"  📋 试卷数量: {paper_count}")
            self.log(f"  ❓ 题目数量: {question_count}")
            self.log(f"  🔗 试卷-题目关联: {paper_question_count}")
            
            # 检查用户数据
            with open("user_management/users.json", 'r', encoding='utf-8') as f:
                user_data = json.load(f)
                user_count = len(user_data.get("users", []))
                
            self.log(f"  👥 用户数量: {user_count}")
            
            # 检查测试用户
            test_users = ["student", "test"]
            found_users = []
            for user in user_data.get("users", []):
                if user.get("username") in test_users:
                    found_users.append(user.get("username"))
                    
            self.log(f"  🧪 测试用户: {found_users}")
            
            success = paper_count > 0 and question_count > 0 and len(found_users) >= 2
            
            self.test_results["tests"]["database_content"] = {
                "status": "PASS" if success else "FAIL",
                "details": {
                    "papers": paper_count,
                    "questions": question_count,
                    "users": user_count,
                    "test_users": found_users
                }
            }
            
            return success
            
        except Exception as e:
            self.log(f"  ❌ 数据库检查失败: {e}", "ERROR")
            self.test_results["tests"]["database_content"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    def test_exam_availability(self):
        """测试3: 考试可用性检查"""
        self.log("📝 测试3: 考试可用性检查")
        
        try:
            with open("client/available_exams.json", 'r', encoding='utf-8') as f:
                exams = json.load(f)
                
            exam_count = len(exams)
            self.log(f"  📊 可用考试数量: {exam_count}")
            
            available_exams = [exam for exam in exams if exam.get("status") == "available"]
            self.log(f"  ✅ 可参加考试: {len(available_exams)}")
            
            for i, exam in enumerate(available_exams[:3], 1):
                self.log(f"    {i}. {exam.get('name', 'Unknown')} ({exam.get('time_limit', 0)}分钟)")
                
            success = len(available_exams) > 0
            
            self.test_results["tests"]["exam_availability"] = {
                "status": "PASS" if success else "FAIL",
                "details": {
                    "total_exams": exam_count,
                    "available_exams": len(available_exams)
                }
            }
            
            return success
            
        except Exception as e:
            self.log(f"  ❌ 考试列表检查失败: {e}", "ERROR")
            self.test_results["tests"]["exam_availability"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    def test_user_authentication(self):
        """测试4: 用户认证测试"""
        self.log("🔐 测试4: 用户认证测试")
        
        try:
            # 模拟登录验证
            sys.path.append('client')
            import api
            
            test_credentials = [
                ("student", "123456"),
                ("test", "123"),
                ("admin", "123456")
            ]
            
            successful_logins = 0
            
            for username, password in test_credentials:
                try:
                    result = api.login(username, password)
                    if result and result.get("username"):
                        self.log(f"  ✅ {username}: 登录成功 (角色: {result.get('role')})")
                        successful_logins += 1
                    else:
                        self.log(f"  ❌ {username}: 登录失败")
                except Exception as e:
                    self.log(f"  ❌ {username}: 登录异常 - {e}")
            
            success = successful_logins >= 2
            
            self.test_results["tests"]["user_authentication"] = {
                "status": "PASS" if success else "FAIL",
                "details": {
                    "successful_logins": successful_logins,
                    "total_attempts": len(test_credentials)
                }
            }
            
            return success
            
        except Exception as e:
            self.log(f"  ❌ 用户认证测试失败: {e}", "ERROR")
            self.test_results["tests"]["user_authentication"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    def test_data_flow(self):
        """测试5: 数据流转测试"""
        self.log("🔄 测试5: 数据流转测试")
        
        try:
            # 检查目录结构
            required_dirs = [
                "exam_management/results",
                "grading_center/queue",
                "grading_center/graded",
                "score_statistics"
            ]
            
            dir_checks = {}
            for dir_path in required_dirs:
                exists = os.path.exists(dir_path)
                dir_checks[dir_path] = exists
                status = "✅" if exists else "❌"
                self.log(f"  {status} {dir_path}")
            
            success = all(dir_checks.values())
            
            self.test_results["tests"]["data_flow"] = {
                "status": "PASS" if success else "FAIL",
                "details": dir_checks
            }
            
            return success
            
        except Exception as e:
            self.log(f"  ❌ 数据流转测试失败: {e}", "ERROR")
            self.test_results["tests"]["data_flow"] = {
                "status": "FAIL",
                "error": str(e)
            }
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        self.log("🚀 开始PH&RL考试系统全流程测试")
        self.log("=" * 60)
        
        tests = [
            self.test_environment_setup,
            self.test_database_content,
            self.test_exam_availability,
            self.test_user_authentication,
            self.test_data_flow
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
                self.log("")  # 空行分隔
            except Exception as e:
                self.log(f"测试执行异常: {e}", "ERROR")
                self.log("")
        
        # 生成测试报告
        self.test_results["end_time"] = datetime.now().isoformat()
        self.test_results["overall_status"] = "PASS" if passed_tests == total_tests else "FAIL"
        self.test_results["summary"] = {
            "passed": passed_tests,
            "total": total_tests,
            "pass_rate": f"{(passed_tests/total_tests)*100:.1f}%"
        }
        
        self.log("=" * 60)
        self.log("📊 测试结果摘要")
        self.log(f"  通过测试: {passed_tests}/{total_tests}")
        self.log(f"  通过率: {(passed_tests/total_tests)*100:.1f}%")
        self.log(f"  总体状态: {'✅ 通过' if passed_tests == total_tests else '❌ 失败'}")
        
        # 保存测试报告
        with open("test_report.json", 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        self.log(f"📄 详细测试报告已保存到: test_report.json")
        
        return passed_tests == total_tests

def main():
    """主函数"""
    print("PH&RL 在线考试系统 - 全流程自动化测试")
    print("基于 COMPLETE_EXAM_FLOW_TEST.md")
    print()
    
    tester = FullFlowTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 所有测试通过！系统准备就绪，可以进行手动测试。")
        print("\n下一步建议:")
        print("1. 运行客户端: python client/client_app.py")
        print("2. 使用测试账户登录: student/123456 或 test/123")
        print("3. 选择考试并完成答题流程")
    else:
        print("\n❌ 部分测试失败，请检查系统配置。")
        print("详细信息请查看 test_report.json")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
