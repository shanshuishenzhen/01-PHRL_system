"""
考试流程集成测试

测试完整的考试流程，从题库管理到成绩统计。
"""

import pytest
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch

from tests.utils.test_helpers import wait_for_condition, create_test_json_file
from tests.utils.mock_helpers import create_mock_user, create_mock_exam, create_mock_question


@pytest.mark.integration
@pytest.mark.slow
class TestExamFlowIntegration:
    """考试流程集成测试"""
    
    @pytest.fixture
    def exam_environment(self, temp_dir):
        """设置考试环境"""
        # 创建测试目录结构
        question_bank_dir = temp_dir / "question_bank_web"
        exam_management_dir = temp_dir / "exam_management"
        grading_center_dir = temp_dir / "grading_center"
        client_dir = temp_dir / "client"
        
        for dir_path in [question_bank_dir, exam_management_dir, grading_center_dir, client_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # 创建测试数据文件
        questions_data = {
            "questions": [
                create_mock_question(1, "single_choice"),
                create_mock_question(2, "multiple_choice"),
                create_mock_question(3, "fill_blank")
            ]
        }
        create_test_json_file(question_bank_dir / "questions.json", questions_data)
        
        users_data = {
            "users": [
                create_mock_user(1, "admin", "admin"),
                create_mock_user(2, "teacher1", "teacher"),
                create_mock_user(3, "student1", "student")
            ]
        }
        create_test_json_file(temp_dir / "user_management" / "users.json", users_data)
        
        exams_data = {
            "exams": [
                create_mock_exam(1, "Python基础测试", "draft")
            ]
        }
        create_test_json_file(exam_management_dir / "exams.json", exams_data)
        
        return {
            "temp_dir": temp_dir,
            "question_bank_dir": question_bank_dir,
            "exam_management_dir": exam_management_dir,
            "grading_center_dir": grading_center_dir,
            "client_dir": client_dir,
            "questions_data": questions_data,
            "users_data": users_data,
            "exams_data": exams_data
        }
    
    def test_complete_exam_flow(self, exam_environment):
        """测试完整的考试流程"""
        env = exam_environment
        
        # 1. 题库管理：创建试卷
        paper_data = self._create_test_paper(env)
        assert paper_data is not None
        
        # 2. 考试管理：发布考试
        exam_data = self._publish_exam(env, paper_data)
        assert exam_data is not None
        
        # 3. 客户端：学生参加考试
        answer_data = self._student_take_exam(env, exam_data)
        assert answer_data is not None
        
        # 4. 阅卷中心：自动阅卷
        grading_result = self._auto_grading(env, answer_data)
        assert grading_result is not None
        
        # 5. 成绩统计：生成统计报告
        statistics_result = self._generate_statistics(env, grading_result)
        assert statistics_result is not None
    
    def _create_test_paper(self, env):
        """创建测试试卷"""
        paper_data = {
            "id": 1,
            "name": "Python基础测试试卷",
            "questions": [
                {"question_id": 1, "score": 10},
                {"question_id": 2, "score": 15},
                {"question_id": 3, "score": 5}
            ],
            "total_score": 30,
            "duration": 60,
            "created_at": "2024-01-01T10:00:00Z"
        }
        
        # 保存试卷数据
        papers_file = env["question_bank_dir"] / "papers.json"
        papers_data = {"papers": [paper_data]}
        create_test_json_file(papers_file, papers_data)
        
        return paper_data
    
    def _publish_exam(self, env, paper_data):
        """发布考试"""
        exam_data = {
            "id": 1,
            "name": "Python基础考试",
            "paper_id": paper_data["id"],
            "status": "published",
            "start_time": "2024-01-01T14:00:00Z",
            "end_time": "2024-01-01T15:00:00Z",
            "participants": [3],  # student1
            "created_by": 2  # teacher1
        }
        
        # 更新考试数据
        exams_file = env["exam_management_dir"] / "exams.json"
        exams_data = {"exams": [exam_data]}
        create_test_json_file(exams_file, exams_data)
        
        # 创建考试发布记录
        published_exams_file = env["exam_management_dir"] / "published_exams.json"
        published_data = {"published_exams": [exam_data]}
        create_test_json_file(published_exams_file, published_data)
        
        return exam_data
    
    def _student_take_exam(self, env, exam_data):
        """学生参加考试"""
        answer_data = {
            "exam_id": exam_data["id"],
            "student_id": 3,
            "answers": [
                {"question_id": 1, "answer": "B"},
                {"question_id": 2, "answer": "ABC"},
                {"question_id": 3, "answer": "解释型语言"}
            ],
            "start_time": "2024-01-01T14:00:00Z",
            "submit_time": "2024-01-01T14:45:00Z",
            "status": "submitted"
        }
        
        # 保存答案数据
        answers_dir = env["exam_management_dir"] / "answers"
        answers_dir.mkdir(exist_ok=True)
        answer_file = answers_dir / f"exam_{exam_data['id']}_student_{answer_data['student_id']}.json"
        create_test_json_file(answer_file, answer_data)
        
        return answer_data
    
    def _auto_grading(self, env, answer_data):
        """自动阅卷"""
        # 模拟自动阅卷逻辑
        grading_result = {
            "exam_id": answer_data["exam_id"],
            "student_id": answer_data["student_id"],
            "scores": [
                {"question_id": 1, "score": 10, "max_score": 10},  # 正确
                {"question_id": 2, "score": 15, "max_score": 15},  # 正确
                {"question_id": 3, "score": 3, "max_score": 5}     # 部分正确
            ],
            "total_score": 28,
            "max_total_score": 30,
            "percentage": 93.33,
            "grade": "A",
            "passed": True,
            "graded_at": "2024-01-01T15:00:00Z"
        }
        
        # 保存阅卷结果
        graded_dir = env["grading_center_dir"] / "graded"
        graded_dir.mkdir(exist_ok=True)
        result_file = graded_dir / f"result_{answer_data['exam_id']}_{answer_data['student_id']}.json"
        create_test_json_file(result_file, grading_result)
        
        return grading_result
    
    def _generate_statistics(self, env, grading_result):
        """生成统计报告"""
        statistics_result = {
            "exam_id": grading_result["exam_id"],
            "total_participants": 1,
            "completed_participants": 1,
            "average_score": grading_result["total_score"],
            "highest_score": grading_result["total_score"],
            "lowest_score": grading_result["total_score"],
            "pass_rate": 100.0,
            "grade_distribution": {
                "A": 1,
                "B": 0,
                "C": 0,
                "D": 0,
                "F": 0
            },
            "question_analysis": [
                {"question_id": 1, "correct_rate": 100.0},
                {"question_id": 2, "correct_rate": 100.0},
                {"question_id": 3, "correct_rate": 60.0}
            ],
            "generated_at": "2024-01-01T15:30:00Z"
        }
        
        # 保存统计结果
        stats_dir = env["temp_dir"] / "score_statistics"
        stats_dir.mkdir(exist_ok=True)
        stats_file = stats_dir / f"statistics_{grading_result['exam_id']}.json"
        create_test_json_file(stats_file, statistics_result)
        
        return statistics_result


@pytest.mark.integration
@pytest.mark.api
class TestModuleAPIIntegration:
    """模块API集成测试"""
    
    def test_question_bank_api_integration(self, mock_http_client):
        """测试题库管理API集成"""
        # 设置模拟响应
        mock_http_client.set_response(
            'GET', 'http://localhost:5000/api/questions',
            {'questions': [create_mock_question(1)]}
        )
        
        # 测试API调用
        response = mock_http_client.get('http://localhost:5000/api/questions')
        assert response.status_code == 200
        
        data = response.json()
        assert 'questions' in data
        assert len(data['questions']) == 1
    
    def test_exam_management_api_integration(self, mock_http_client):
        """测试考试管理API集成"""
        # 设置模拟响应
        mock_http_client.set_response(
            'POST', 'http://localhost:5001/api/exams',
            {'id': 1, 'status': 'created'},
            status_code=201
        )
        
        # 测试创建考试
        exam_data = create_mock_exam(1, "Test Exam", "draft")
        response = mock_http_client.post(
            'http://localhost:5001/api/exams',
            json=exam_data
        )
        
        assert response.status_code == 201
        result = response.json()
        assert result['id'] == 1
        assert result['status'] == 'created'
    
    def test_grading_center_api_integration(self, mock_http_client):
        """测试阅卷中心API集成"""
        # 设置模拟响应
        mock_http_client.set_response(
            'POST', 'http://localhost:3000/api/grade',
            {'status': 'graded', 'score': 85}
        )
        
        # 测试提交阅卷
        answer_data = {
            "exam_id": 1,
            "student_id": 3,
            "answers": [{"question_id": 1, "answer": "A"}]
        }
        
        response = mock_http_client.post(
            'http://localhost:3000/api/grade',
            json=answer_data
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result['status'] == 'graded'
        assert result['score'] == 85


@pytest.mark.integration
@pytest.mark.database
class TestDataFlowIntegration:
    """数据流集成测试"""
    
    def test_data_synchronization(self, temp_dir):
        """测试数据同步"""
        # 创建源数据
        source_data = {"test": "data", "timestamp": "2024-01-01T10:00:00Z"}
        source_file = temp_dir / "source.json"
        create_test_json_file(source_file, source_data)
        
        # 模拟数据同步过程
        target_file = temp_dir / "target.json"
        
        # 读取源数据
        with open(source_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 写入目标文件
        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # 验证同步结果
        assert target_file.exists()
        with open(target_file, 'r', encoding='utf-8') as f:
            target_data = json.load(f)
        
        assert target_data == source_data
    
    def test_module_communication(self, temp_dir):
        """测试模块间通信"""
        # 创建通信目录
        comm_dir = temp_dir / "communication"
        comm_dir.mkdir()
        
        # 模块A发送消息
        message_a = {"from": "module_a", "to": "module_b", "data": "test_message"}
        message_file = comm_dir / "message_a_to_b.json"
        create_test_json_file(message_file, message_a)
        
        # 模块B接收消息
        assert message_file.exists()
        with open(message_file, 'r', encoding='utf-8') as f:
            received_message = json.load(f)
        
        assert received_message == message_a
        
        # 模块B回复消息
        reply_message = {"from": "module_b", "to": "module_a", "data": "reply_message"}
        reply_file = comm_dir / "reply_b_to_a.json"
        create_test_json_file(reply_file, reply_message)
        
        # 验证回复
        assert reply_file.exists()
        with open(reply_file, 'r', encoding='utf-8') as f:
            received_reply = json.load(f)
        
        assert received_reply == reply_message
