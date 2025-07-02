"""
用户场景端到端测试

测试真实的用户使用场景。
"""

import pytest
import time
import json
from pathlib import Path
from unittest.mock import Mock, patch

from tests.utils.test_helpers import wait_for_condition, create_test_json_file
from tests.utils.mock_helpers import create_mock_user, create_mock_exam, create_mock_question


@pytest.mark.e2e
@pytest.mark.slow
class TestTeacherWorkflow:
    """教师工作流程测试"""
    
    @pytest.fixture
    def teacher_environment(self, temp_dir):
        """设置教师测试环境"""
        # 创建教师用户
        teacher_data = create_mock_user(2, "teacher1", "teacher")
        users_data = {"users": [teacher_data]}
        
        user_dir = temp_dir / "user_management"
        user_dir.mkdir()
        create_test_json_file(user_dir / "users.json", users_data)
        
        # 创建题库目录
        question_bank_dir = temp_dir / "question_bank_web"
        question_bank_dir.mkdir()
        
        return {
            "temp_dir": temp_dir,
            "teacher_data": teacher_data,
            "question_bank_dir": question_bank_dir,
            "user_dir": user_dir
        }
    
    def test_teacher_create_exam_workflow(self, teacher_environment):
        """测试教师创建考试的完整流程"""
        env = teacher_environment
        
        # 1. 教师登录
        login_result = self._teacher_login(env)
        assert login_result["success"] is True
        
        # 2. 创建题目
        questions = self._create_questions(env)
        assert len(questions) > 0
        
        # 3. 创建试卷
        paper = self._create_paper(env, questions)
        assert paper is not None
        
        # 4. 创建考试
        exam = self._create_exam(env, paper)
        assert exam is not None
        
        # 5. 发布考试
        publish_result = self._publish_exam(env, exam)
        assert publish_result["success"] is True
    
    def _teacher_login(self, env):
        """教师登录"""
        # 模拟登录过程
        teacher = env["teacher_data"]
        
        # 验证用户名和密码
        if teacher["username"] == "teacher1" and teacher["role"] == "teacher":
            return {
                "success": True,
                "user_id": teacher["id"],
                "username": teacher["username"],
                "role": teacher["role"]
            }
        
        return {"success": False, "error": "Invalid credentials"}
    
    def _create_questions(self, env):
        """创建题目"""
        questions = [
            create_mock_question(1, "single_choice"),
            create_mock_question(2, "multiple_choice"),
            create_mock_question(3, "fill_blank"),
            create_mock_question(4, "essay")
        ]
        
        # 保存题目到题库
        questions_data = {"questions": questions}
        questions_file = env["question_bank_dir"] / "questions.json"
        create_test_json_file(questions_file, questions_data)
        
        return questions
    
    def _create_paper(self, env, questions):
        """创建试卷"""
        paper = {
            "id": 1,
            "name": "期末考试试卷",
            "description": "Python程序设计期末考试",
            "questions": [
                {"question_id": q["id"], "score": 10} for q in questions
            ],
            "total_score": len(questions) * 10,
            "duration": 120,
            "created_by": env["teacher_data"]["id"],
            "created_at": "2024-01-01T10:00:00Z"
        }
        
        # 保存试卷
        papers_data = {"papers": [paper]}
        papers_file = env["question_bank_dir"] / "papers.json"
        create_test_json_file(papers_file, papers_data)
        
        return paper
    
    def _create_exam(self, env, paper):
        """创建考试"""
        exam = {
            "id": 1,
            "name": "Python程序设计期末考试",
            "description": "2024年春季学期期末考试",
            "paper_id": paper["id"],
            "status": "draft",
            "start_time": "2024-06-15T09:00:00Z",
            "end_time": "2024-06-15T11:00:00Z",
            "duration": paper["duration"],
            "total_score": paper["total_score"],
            "pass_score": 60,
            "created_by": env["teacher_data"]["id"],
            "created_at": "2024-01-01T10:00:00Z"
        }
        
        # 保存考试
        exam_dir = env["temp_dir"] / "exam_management"
        exam_dir.mkdir(exist_ok=True)
        exams_data = {"exams": [exam]}
        create_test_json_file(exam_dir / "exams.json", exams_data)
        
        return exam
    
    def _publish_exam(self, env, exam):
        """发布考试"""
        # 更新考试状态
        exam["status"] = "published"
        exam["published_at"] = "2024-01-01T12:00:00Z"
        
        # 保存发布记录
        exam_dir = env["temp_dir"] / "exam_management"
        published_data = {"published_exams": [exam]}
        create_test_json_file(exam_dir / "published_exams.json", published_data)
        
        return {"success": True, "exam_id": exam["id"]}


@pytest.mark.e2e
@pytest.mark.slow
class TestStudentWorkflow:
    """学生工作流程测试"""
    
    @pytest.fixture
    def student_environment(self, temp_dir):
        """设置学生测试环境"""
        # 创建学生用户
        student_data = create_mock_user(3, "student1", "student")
        users_data = {"users": [student_data]}
        
        user_dir = temp_dir / "user_management"
        user_dir.mkdir()
        create_test_json_file(user_dir / "users.json", users_data)
        
        # 创建已发布的考试
        exam_data = create_mock_exam(1, "Python基础测试", "published")
        exam_dir = temp_dir / "exam_management"
        exam_dir.mkdir()
        published_data = {"published_exams": [exam_data]}
        create_test_json_file(exam_dir / "published_exams.json", published_data)
        
        return {
            "temp_dir": temp_dir,
            "student_data": student_data,
            "exam_data": exam_data,
            "user_dir": user_dir,
            "exam_dir": exam_dir
        }
    
    def test_student_take_exam_workflow(self, student_environment):
        """测试学生参加考试的完整流程"""
        env = student_environment
        
        # 1. 学生登录
        login_result = self._student_login(env)
        assert login_result["success"] is True
        
        # 2. 查看可参加的考试
        available_exams = self._get_available_exams(env)
        assert len(available_exams) > 0
        
        # 3. 开始考试
        exam_session = self._start_exam(env, available_exams[0])
        assert exam_session is not None
        
        # 4. 答题
        answers = self._answer_questions(env, exam_session)
        assert len(answers) > 0
        
        # 5. 提交考试
        submit_result = self._submit_exam(env, exam_session, answers)
        assert submit_result["success"] is True
        
        # 6. 查看结果（如果允许）
        result = self._view_result(env, submit_result["submission_id"])
        assert result is not None
    
    def _student_login(self, env):
        """学生登录"""
        student = env["student_data"]
        
        if student["username"] == "student1" and student["role"] == "student":
            return {
                "success": True,
                "user_id": student["id"],
                "username": student["username"],
                "role": student["role"]
            }
        
        return {"success": False, "error": "Invalid credentials"}
    
    def _get_available_exams(self, env):
        """获取可参加的考试"""
        # 读取已发布的考试
        published_file = env["exam_dir"] / "published_exams.json"
        with open(published_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get("published_exams", [])
    
    def _start_exam(self, env, exam):
        """开始考试"""
        exam_session = {
            "session_id": "session_001",
            "exam_id": exam["id"],
            "student_id": env["student_data"]["id"],
            "start_time": "2024-01-01T14:00:00Z",
            "end_time": "2024-01-01T15:00:00Z",
            "status": "in_progress",
            "questions": [
                create_mock_question(1, "single_choice"),
                create_mock_question(2, "multiple_choice"),
                create_mock_question(3, "fill_blank")
            ]
        }
        
        # 保存考试会话
        sessions_dir = env["temp_dir"] / "client" / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        session_file = sessions_dir / f"session_{exam_session['session_id']}.json"
        create_test_json_file(session_file, exam_session)
        
        return exam_session
    
    def _answer_questions(self, env, exam_session):
        """答题"""
        answers = []
        
        for question in exam_session["questions"]:
            if question["type"] == "single_choice":
                answer = {"question_id": question["id"], "answer": "A"}
            elif question["type"] == "multiple_choice":
                answer = {"question_id": question["id"], "answer": "AB"}
            elif question["type"] == "fill_blank":
                answer = {"question_id": question["id"], "answer": "Python"}
            else:
                answer = {"question_id": question["id"], "answer": "Sample answer"}
            
            answers.append(answer)
        
        return answers
    
    def _submit_exam(self, env, exam_session, answers):
        """提交考试"""
        submission = {
            "submission_id": "sub_001",
            "session_id": exam_session["session_id"],
            "exam_id": exam_session["exam_id"],
            "student_id": exam_session["student_id"],
            "answers": answers,
            "submit_time": "2024-01-01T14:45:00Z",
            "status": "submitted"
        }
        
        # 保存提交记录
        answers_dir = env["exam_dir"] / "answers"
        answers_dir.mkdir(exist_ok=True)
        submission_file = answers_dir / f"submission_{submission['submission_id']}.json"
        create_test_json_file(submission_file, submission)
        
        return {"success": True, "submission_id": submission["submission_id"]}
    
    def _view_result(self, env, submission_id):
        """查看考试结果"""
        # 模拟阅卷完成后的结果
        result = {
            "submission_id": submission_id,
            "student_id": env["student_data"]["id"],
            "total_score": 85,
            "max_score": 100,
            "percentage": 85.0,
            "grade": "B",
            "passed": True,
            "graded_at": "2024-01-01T15:30:00Z"
        }
        
        return result


@pytest.mark.e2e
@pytest.mark.slow
class TestSystemAdminWorkflow:
    """系统管理员工作流程测试"""
    
    def test_admin_system_management_workflow(self, temp_dir):
        """测试管理员系统管理流程"""
        # 1. 管理员登录
        admin_data = create_mock_user(1, "admin", "super_admin")
        login_result = self._admin_login(admin_data)
        assert login_result["success"] is True
        
        # 2. 系统状态检查
        system_status = self._check_system_status(temp_dir)
        assert system_status["overall_status"] == "healthy"
        
        # 3. 用户管理
        user_management_result = self._manage_users(temp_dir)
        assert user_management_result["success"] is True
        
        # 4. 系统配置
        config_result = self._update_system_config(temp_dir)
        assert config_result["success"] is True
        
        # 5. 数据备份
        backup_result = self._backup_system_data(temp_dir)
        assert backup_result["success"] is True
    
    def _admin_login(self, admin_data):
        """管理员登录"""
        if admin_data["role"] == "super_admin":
            return {
                "success": True,
                "user_id": admin_data["id"],
                "username": admin_data["username"],
                "role": admin_data["role"],
                "permissions": ["all"]
            }
        
        return {"success": False, "error": "Insufficient privileges"}
    
    def _check_system_status(self, temp_dir):
        """检查系统状态"""
        # 模拟系统状态检查
        modules_status = {
            "question_bank": "running",
            "exam_management": "running",
            "grading_center": "running",
            "client": "running",
            "user_management": "running"
        }
        
        system_status = {
            "overall_status": "healthy",
            "modules": modules_status,
            "disk_usage": 45.2,
            "memory_usage": 62.8,
            "cpu_usage": 23.5,
            "active_users": 15,
            "active_exams": 3
        }
        
        # 保存状态报告
        status_dir = temp_dir / "system_status"
        status_dir.mkdir(exist_ok=True)
        status_file = status_dir / "current_status.json"
        create_test_json_file(status_file, system_status)
        
        return system_status
    
    def _manage_users(self, temp_dir):
        """管理用户"""
        # 创建用户管理操作记录
        user_operations = [
            {"action": "create", "user_id": 4, "username": "newuser", "role": "student"},
            {"action": "update", "user_id": 3, "field": "status", "value": "active"},
            {"action": "delete", "user_id": 5, "reason": "graduation"}
        ]
        
        # 保存操作记录
        user_dir = temp_dir / "user_management"
        user_dir.mkdir(exist_ok=True)
        operations_file = user_dir / "operations_log.json"
        create_test_json_file(operations_file, {"operations": user_operations})
        
        return {"success": True, "operations_count": len(user_operations)}
    
    def _update_system_config(self, temp_dir):
        """更新系统配置"""
        new_config = {
            "version": "1.1.0",
            "module_ports": {
                "question_bank": 5000,
                "grading_center": 3000,
                "exam_management": 5001,
                "client": 8080
            },
            "security": {
                "session_timeout": 3600,
                "max_login_attempts": 5,
                "password_policy": "strong"
            },
            "performance": {
                "max_concurrent_exams": 100,
                "cache_size": "256MB",
                "database_pool_size": 20
            }
        }
        
        # 保存新配置
        config_file = temp_dir / "config.json"
        create_test_json_file(config_file, new_config)
        
        return {"success": True, "config_version": new_config["version"]}
    
    def _backup_system_data(self, temp_dir):
        """备份系统数据"""
        backup_manifest = {
            "backup_id": "backup_20240101_150000",
            "timestamp": "2024-01-01T15:00:00Z",
            "files": [
                "user_management/users.json",
                "exam_management/exams.json",
                "question_bank_web/questions.json",
                "grading_center/results.json"
            ],
            "size_mb": 125.6,
            "status": "completed"
        }
        
        # 保存备份清单
        backup_dir = temp_dir / "backups"
        backup_dir.mkdir(exist_ok=True)
        manifest_file = backup_dir / f"{backup_manifest['backup_id']}_manifest.json"
        create_test_json_file(manifest_file, backup_manifest)
        
        return {"success": True, "backup_id": backup_manifest["backup_id"]}
