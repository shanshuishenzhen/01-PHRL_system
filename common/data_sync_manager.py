# -*- coding: utf-8 -*-
"""
数据同步管理器

负责各模块间的数据同步和通信，确保考试流程的完整性。

更新日志：
- 2025-01-07：创建数据同步管理器，解决模块间数据流转问题
"""

import os
import sys
import json
import sqlite3
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# 导入项目模块
sys.path.append(str(Path(__file__).parent.parent))
from common.logger import get_logger
from common.config_manager import ConfigManager
from common.error_handler import handle_error, retry
from common.sql_security import ParameterizedQuery


class DataSyncManager:
    """数据同步管理器"""
    
    def __init__(self):
        self.logger = get_logger("data_sync_manager")
        self.config_manager = ConfigManager()
        
        # 数据库路径配置
        self.databases = {
            "question_bank": "question_bank_web/local_dev.db",
            "user_management": "user_management/users.db", 
            "exam_management": "exam_management/exams.json",
            "score_statistics": "score_statistics/scores.json",
            "main": "database.sqlite"
        }
        
        # API端点配置
        self.api_endpoints = {
            "question_bank": "http://localhost:5000",
            "grading_center": "http://localhost:3000",
            "exam_management": "http://localhost:5001"
        }
    
    def sync_published_papers_to_exam_system(self) -> bool:
        """同步已发布的试卷到考试系统"""
        try:
            self.logger.info("开始同步试卷数据...")
            
            # 从题库获取已发布的试卷
            published_papers = self.get_published_papers()
            
            if not published_papers:
                self.logger.warning("没有找到已发布的试卷")
                return True
            
            # 同步到考试管理系统
            for paper in published_papers:
                self.sync_paper_to_exam_management(paper)
            
            # 同步到客户端可见的考试列表
            self.update_available_exams(published_papers)
            
            self.logger.info(f"成功同步 {len(published_papers)} 份试卷")
            return True

        except Exception as e:
            self.logger.error(f"试卷同步失败: {e}")
            return False

    def sync_published_exams_to_client(self) -> bool:
        """
        同步考试发布模块的已发布考试到客户端
        """
        try:
            self.logger.info("开始同步已发布考试到客户端...")

            # 1. 从考试发布模块获取已发布的考试
            published_exams = self.get_published_exams_from_publisher()

            if not published_exams:
                self.logger.warning("没有找到已发布的考试")
                return True

            # 2. 转换为客户端格式并保存
            client_exams = []
            for exam in published_exams:
                if exam.get('status') == 'published':
                    client_exam = self.convert_exam_to_client_format(exam)
                    if client_exam:
                        client_exams.append(client_exam)

            # 3. 保存到客户端考试列表
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            client_exams_file = os.path.join(project_root, 'client', 'available_exams.json')
            os.makedirs(os.path.dirname(client_exams_file), exist_ok=True)

            with open(client_exams_file, 'w', encoding='utf-8') as f:
                json.dump(client_exams, f, ensure_ascii=False, indent=2)

            self.logger.info(f"成功同步 {len(client_exams)} 个已发布考试到客户端")
            return True

        except Exception as e:
            self.logger.error(f"同步已发布考试到客户端失败: {e}")
            return False

    def get_published_exams_from_publisher(self) -> List[Dict]:
        """从考试发布模块获取已发布的考试"""
        try:
            # 使用相对路径
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            published_exams_file = os.path.join(project_root, 'exam_management', 'published_exams.json')

            if os.path.exists(published_exams_file):
                with open(published_exams_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"获取已发布考试失败: {e}")
            return []

    def convert_exam_to_client_format(self, exam: Dict) -> Optional[Dict]:
        """将考试数据转换为客户端格式"""
        try:
            # 获取试卷信息
            paper_info = self.get_paper_info(exam['paper_id'])

            client_exam = {
                "exam_id": exam['id'],
                "paper_id": exam['paper_id'],
                "name": exam['title'],
                "description": exam.get('description', ''),
                "time_limit": exam.get('duration', 60),
                "total_score": exam.get('total_score', 100),
                "status": "available",
                "start_time": exam.get('start_time', ''),
                "end_time": exam.get('end_time', ''),
                "created_at": exam.get('created_at', ''),
                "instructions": "请仔细阅读题目，认真作答。考试时间有限，请合理分配时间。",
                "settings": exam.get('settings', {}),
                "paper_info": paper_info
            }

            return client_exam

        except Exception as e:
            self.logger.error(f"转换考试格式失败: {e}")
            return None

    def get_paper_info(self, paper_id: str) -> Dict:
        """获取试卷信息"""
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(project_root, 'question_bank_web', 'local_dev.db')

            if not os.path.exists(db_path):
                return {}

            db = ParameterizedQuery(db_path)
            papers_raw = db.execute_query("""
                SELECT p.id, p.name, p.description, p.duration, p.total_score,
                       COUNT(pq.question_id) as question_count
                FROM papers p
                LEFT JOIN paper_questions pq ON p.id = pq.paper_id
                WHERE p.id = ?
                GROUP BY p.id, p.name, p.description, p.duration, p.total_score
            """, (paper_id,))

            if papers_raw:
                row = papers_raw[0]
                return {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'duration': row[3],
                    'total_score': row[4],
                    'question_count': row[5]
                }
            return {}

        except Exception as e:
            self.logger.error(f"获取试卷信息失败: {e}")
            return {}
    
    def get_published_papers(self) -> List[Dict]:
        """从题库获取已发布的试卷"""
        try:
            # 尝试通过API获取
            try:
                response = requests.get(f"{self.api_endpoints['question_bank']}/api/papers/published", timeout=5)
                if response.status_code == 200:
                    return response.json()
            except requests.RequestException:
                self.logger.warning("无法通过API获取试卷，尝试直接访问数据库")
            
            # 直接访问数据库
            db_path = self.databases["question_bank"]
            if not os.path.exists(db_path):
                self.logger.warning(f"题库数据库不存在: {db_path}")
                return []
            
            db = ParameterizedQuery(db_path)
            papers = db.execute_query("""
                SELECT p.id, p.name, p.description, p.duration, p.total_score,
                       p.created_at
                FROM papers p
                ORDER BY p.created_at DESC
            """)
            
            return [dict(paper) for paper in papers]
            
        except Exception as e:
            self.logger.error(f"获取试卷失败: {e}")
            return []
    
    def sync_paper_to_exam_management(self, paper: Dict) -> bool:
        """同步试卷到考试管理系统"""
        try:
            # 读取考试管理数据
            exam_file = "exam_management/exams.json"
            if os.path.exists(exam_file):
                with open(exam_file, 'r', encoding='utf-8') as f:
                    exams_data = json.load(f)
            else:
                exams_data = []
            
            # 检查是否已存在
            paper_id = paper.get('id')
            existing_exam = next((e for e in exams_data if e.get('paper_id') == paper_id), None)
            
            if existing_exam:
                # 更新现有考试
                existing_exam.update({
                    'title': paper.get('name', ''),
                    'description': paper.get('description', ''),
                    'time_limit': paper.get('duration', 60),
                    'total_score': paper.get('total_score', 100),
                    'updated_at': datetime.now().isoformat()
                })
                self.logger.info(f"更新考试: {paper.get('name')}")
            else:
                # 创建新考试
                new_exam = {
                    'id': f"exam_{paper_id}_{int(time.time())}",
                    'paper_id': paper_id,
                    'title': paper.get('name', ''),
                    'description': paper.get('description', ''),
                    'time_limit': paper.get('duration', 60),
                    'total_score': paper.get('total_score', 100),
                    'status': 'available',
                    'created_at': datetime.now().isoformat(),
                    'participants': [],
                    'results': []
                }
                exams_data.append(new_exam)
                self.logger.info(f"创建新考试: {paper.get('name')}")
            
            # 保存更新后的数据
            os.makedirs(os.path.dirname(exam_file), exist_ok=True)
            with open(exam_file, 'w', encoding='utf-8') as f:
                json.dump(exams_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"同步试卷到考试管理失败: {e}")
            return False
    
    def update_available_exams(self, papers: List[Dict]) -> bool:
        """更新客户端可见的考试列表"""
        try:
            # 创建客户端考试列表文件
            client_exams_file = "client/available_exams.json"
            
            available_exams = []
            for paper in papers:
                exam_info = {
                    'exam_id': f"exam_{paper.get('id')}",
                    'paper_id': paper.get('id'),
                    'title': paper.get('name', ''),
                    'description': paper.get('description', ''),
                    'time_limit': paper.get('duration', 60),
                    'total_score': paper.get('total_score', 100),
                    'status': 'available',
                    'created_at': paper.get('created_at', ''),
                    'instructions': '请仔细阅读题目，认真作答。考试时间有限，请合理分配时间。'
                }
                available_exams.append(exam_info)
            
            # 保存到客户端目录
            os.makedirs(os.path.dirname(client_exams_file), exist_ok=True)
            with open(client_exams_file, 'w', encoding='utf-8') as f:
                json.dump(available_exams, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"更新客户端考试列表，共 {len(available_exams)} 个考试")
            return True
            
        except Exception as e:
            self.logger.error(f"更新客户端考试列表失败: {e}")
            return False
    
    def get_paper_questions(self, paper_id: int) -> List[Dict]:
        """获取试卷的题目详情"""
        try:
            db_path = self.databases["question_bank"]
            if not os.path.exists(db_path):
                return []
            
            db = ParameterizedQuery(db_path)
            questions = db.execute_query("""
                SELECT q.id, q.content, q.question_type, q.options, q.correct_answer, 
                       q.score, pq.question_order
                FROM questions q
                JOIN paper_questions pq ON q.id = pq.question_id
                WHERE pq.paper_id = :paper_id
                ORDER BY pq.question_order
            """, {"paper_id": paper_id})
            
            return [dict(question) for question in questions]
            
        except Exception as e:
            self.logger.error(f"获取试卷题目失败: {e}")
            return []
    
    @retry(max_attempts=3, delay=1.0)
    def submit_exam_result(self, exam_result: Dict) -> bool:
        """提交考试结果到阅卷中心"""
        try:
            # 保存到本地
            results_dir = "exam_management/results"
            os.makedirs(results_dir, exist_ok=True)
            
            result_file = os.path.join(results_dir, f"result_{exam_result['exam_id']}_{exam_result['user_id']}.json")
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(exam_result, f, ensure_ascii=False, indent=2)
            
            # 尝试提交到阅卷中心API
            try:
                response = requests.post(
                    f"{self.api_endpoints['grading_center']}/api/submit_result",
                    json=exam_result,
                    timeout=10
                )
                if response.status_code == 200:
                    self.logger.info(f"考试结果已提交到阅卷中心: {exam_result['exam_id']}")
                    return True
            except requests.RequestException as e:
                self.logger.warning(f"无法连接阅卷中心API，结果已保存到本地: {e}")
            
            # 如果API不可用，保存到阅卷中心的待处理目录
            grading_queue_dir = "grading_center/queue"
            os.makedirs(grading_queue_dir, exist_ok=True)
            
            queue_file = os.path.join(grading_queue_dir, f"pending_{int(time.time())}_{exam_result['user_id']}.json")
            with open(queue_file, 'w', encoding='utf-8') as f:
                json.dump(exam_result, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"考试结果已保存到阅卷队列: {queue_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"提交考试结果失败: {e}")
            return False
    
    def sync_grading_results_to_statistics(self) -> bool:
        """同步阅卷结果到成绩统计模块"""
        try:
            # 获取阅卷完成的结果
            graded_results = self.get_graded_results()
            
            if not graded_results:
                self.logger.info("没有新的阅卷结果需要同步")
                return True
            
            # 读取成绩统计数据
            scores_file = "score_statistics/scores.json"
            if os.path.exists(scores_file):
                with open(scores_file, 'r', encoding='utf-8') as f:
                    scores_data = json.load(f)
            else:
                scores_data = []
            
            # 添加新的成绩记录
            for result in graded_results:
                score_record = {
                    'id': f"score_{result['exam_id']}_{result['user_id']}",
                    'exam_id': result['exam_id'],
                    'user_id': result['user_id'],
                    'user_name': result.get('user_name', ''),
                    'paper_title': result.get('paper_title', ''),
                    'total_score': result.get('total_score', 0),
                    'obtained_score': result.get('final_score', 0),
                    'percentage': round((result.get('final_score', 0) / result.get('total_score', 1)) * 100, 2),
                    'grade': self.calculate_grade(result.get('final_score', 0), result.get('total_score', 1)),
                    'exam_time': result.get('submit_time', ''),
                    'grading_time': result.get('grading_time', ''),
                    'details': result.get('question_scores', [])
                }
                scores_data.append(score_record)
            
            # 保存更新后的成绩数据
            os.makedirs(os.path.dirname(scores_file), exist_ok=True)
            with open(scores_file, 'w', encoding='utf-8') as f:
                json.dump(scores_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"成功同步 {len(graded_results)} 条阅卷结果到成绩统计")
            return True
            
        except Exception as e:
            self.logger.error(f"同步阅卷结果失败: {e}")
            return False
    
    def get_graded_results(self) -> List[Dict]:
        """获取已完成阅卷的结果"""
        try:
            graded_results = []
            
            # 检查阅卷中心的完成目录
            graded_dir = "grading_center/graded"
            if os.path.exists(graded_dir):
                for file_name in os.listdir(graded_dir):
                    if file_name.endswith('.json'):
                        file_path = os.path.join(graded_dir, file_name)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                result = json.load(f)
                                graded_results.append(result)
                            
                            # 移动到已处理目录
                            processed_dir = "grading_center/processed"
                            os.makedirs(processed_dir, exist_ok=True)
                            os.rename(file_path, os.path.join(processed_dir, file_name))
                            
                        except Exception as e:
                            self.logger.error(f"处理阅卷结果文件失败 {file_name}: {e}")
            
            return graded_results
            
        except Exception as e:
            self.logger.error(f"获取阅卷结果失败: {e}")
            return []
    
    def calculate_grade(self, obtained_score: float, total_score: float) -> str:
        """计算等级"""
        if total_score <= 0:
            return "无效"
        
        percentage = (obtained_score / total_score) * 100
        
        if percentage >= 90:
            return "优秀"
        elif percentage >= 80:
            return "良好"
        elif percentage >= 70:
            return "中等"
        elif percentage >= 60:
            return "及格"
        else:
            return "不及格"
    
    def run_full_sync(self) -> bool:
        """运行完整的数据同步"""
        try:
            self.logger.info("开始完整数据同步...")
            
            # 1. 同步试卷到考试系统
            if not self.sync_published_papers_to_exam_system():
                self.logger.error("试卷同步失败")
                return False
            
            # 2. 同步阅卷结果到成绩统计
            if not self.sync_grading_results_to_statistics():
                self.logger.error("阅卷结果同步失败")
                return False
            
            self.logger.info("完整数据同步完成")
            return True
            
        except Exception as e:
            self.logger.error(f"完整数据同步失败: {e}")
            return False


if __name__ == "__main__":
    # 运行数据同步
    sync_manager = DataSyncManager()
    success = sync_manager.run_full_sync()
    
    if success:
        print("✅ 数据同步完成")
    else:
        print("❌ 数据同步失败")
