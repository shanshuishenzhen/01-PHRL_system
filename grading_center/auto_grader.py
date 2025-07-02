# -*- coding: utf-8 -*-
"""
自动阅卷系统

负责自动批改客观题，处理主观题，生成阅卷结果。

更新日志：
- 2025-01-07：创建自动阅卷系统
"""

import os
import sys
import json
import sqlite3
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# 导入项目模块
sys.path.append(str(Path(__file__).parent.parent))
from common.logger import get_logger
from common.error_handler import handle_error, retry
from common.sql_security import ParameterizedQuery


class AutoGrader:
    """自动阅卷器"""
    
    def __init__(self):
        self.logger = get_logger("auto_grader")
        self.queue_dir = Path(__file__).parent / "queue"
        self.graded_dir = Path(__file__).parent / "graded"
        self.processed_dir = Path(__file__).parent / "processed"
        
        # 确保目录存在
        self.queue_dir.mkdir(exist_ok=True)
        self.graded_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)
    
    def process_pending_exams(self) -> int:
        """处理待阅卷的考试"""
        processed_count = 0
        
        try:
            # 获取队列中的所有待处理文件
            pending_files = list(self.queue_dir.glob("*.json"))
            
            if not pending_files:
                self.logger.info("没有待处理的考试结果")
                return 0
            
            self.logger.info(f"发现 {len(pending_files)} 个待处理的考试结果")
            
            for file_path in pending_files:
                try:
                    success = self.grade_single_exam(file_path)
                    if success:
                        processed_count += 1
                        # 移动到已处理目录
                        processed_file = self.processed_dir / file_path.name
                        file_path.rename(processed_file)
                        self.logger.info(f"考试结果处理完成: {file_path.name}")
                    else:
                        self.logger.error(f"考试结果处理失败: {file_path.name}")
                        
                except Exception as e:
                    self.logger.error(f"处理考试文件失败 {file_path.name}: {e}")
            
            return processed_count
            
        except Exception as e:
            self.logger.error(f"处理待阅卷考试失败: {e}")
            return processed_count
    
    def grade_single_exam(self, file_path: Path) -> bool:
        """阅卷单个考试"""
        try:
            # 读取考试结果
            with open(file_path, 'r', encoding='utf-8') as f:
                exam_result = json.load(f)
            
            exam_id = exam_result.get('exam_id')
            user_id = exam_result.get('user_id')
            answers = exam_result.get('answers', {})
            
            self.logger.info(f"开始阅卷: 考试ID={exam_id}, 用户ID={user_id}")
            
            # 获取考试的正确答案
            correct_answers = self.get_correct_answers(exam_id)
            if not correct_answers:
                self.logger.warning(f"无法获取考试 {exam_id} 的正确答案，使用默认评分")
                return self.create_default_grading_result(exam_result, file_path)
            
            # 进行自动阅卷
            grading_result = self.auto_grade_answers(answers, correct_answers)
            
            # 生成最终阅卷结果
            final_result = {
                "exam_id": exam_id,
                "user_id": user_id,
                "user_name": exam_result.get('user_name', ''),
                "username": exam_result.get('username', ''),
                "department": exam_result.get('department', ''),
                "paper_title": correct_answers.get('paper_title', ''),
                "submit_time": exam_result.get('submit_time'),
                "grading_time": datetime.now().isoformat(),
                "total_score": correct_answers.get('total_score', 100),
                "obtained_score": grading_result['total_obtained_score'],
                "final_score": grading_result['total_obtained_score'],
                "percentage": round((grading_result['total_obtained_score'] / correct_answers.get('total_score', 100)) * 100, 2),
                "question_scores": grading_result['question_scores'],
                "grading_details": grading_result['grading_details'],
                "auto_graded": True,
                "grader": "auto_grader_v1.0"
            }
            
            # 保存阅卷结果
            graded_file = self.graded_dir / f"graded_{exam_id}_{user_id}_{int(time.time())}.json"
            with open(graded_file, 'w', encoding='utf-8') as f:
                json.dump(final_result, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"阅卷完成: {graded_file.name}, 得分: {final_result['final_score']}/{final_result['total_score']}")
            return True
            
        except Exception as e:
            self.logger.error(f"阅卷失败: {e}")
            return False
    
    def get_correct_answers(self, exam_id) -> Optional[Dict]:
        """获取考试的正确答案"""
        try:
            # 尝试从题库数据库获取正确答案
            paper_id = self.extract_paper_id(exam_id)
            if paper_id:
                return self.get_answers_from_question_bank(paper_id)
            
            # 如果无法从题库获取，尝试从考试管理数据获取
            return self.get_answers_from_exam_data(exam_id)
            
        except Exception as e:
            self.logger.error(f"获取正确答案失败: {e}")
            return None
    
    def extract_paper_id(self, exam_id) -> Optional[int]:
        """从exam_id提取paper_id"""
        try:
            if isinstance(exam_id, str) and exam_id.startswith("exam_"):
                parts = exam_id.split("_")
                if len(parts) >= 2:
                    return int(parts[1])
            elif isinstance(exam_id, (int, str)) and str(exam_id).isdigit():
                return int(exam_id)
        except:
            pass
        return None
    
    def get_answers_from_question_bank(self, paper_id: int) -> Optional[Dict]:
        """从题库数据库获取正确答案"""
        try:
            db_path = Path(__file__).parent.parent / "question_bank_web" / "local_dev.db"
            if not db_path.exists():
                return None
            
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 获取试卷信息
            cursor.execute("""
                SELECT title, total_score, time_limit
                FROM papers 
                WHERE id = ?
            """, (paper_id,))
            
            paper = cursor.fetchone()
            if not paper:
                conn.close()
                return None
            
            # 获取题目和答案
            cursor.execute("""
                SELECT q.id, q.content, q.question_type, q.correct_answer, 
                       q.score, pq.question_order
                FROM questions q
                JOIN paper_questions pq ON q.id = pq.question_id
                WHERE pq.paper_id = ?
                ORDER BY pq.question_order
            """, (paper_id,))
            
            questions = cursor.fetchall()
            conn.close()
            
            if not questions:
                return None
            
            # 构建答案字典
            correct_answers = {
                "paper_id": paper_id,
                "paper_title": paper['title'],
                "total_score": paper['total_score'] or 100,
                "questions": {}
            }
            
            for q in questions:
                question_id = str(q['id'])
                correct_answers["questions"][question_id] = {
                    "correct_answer": q['correct_answer'],
                    "question_type": q['question_type'],
                    "score": q['score'] or 10,
                    "content": q['content']
                }
            
            return correct_answers
            
        except Exception as e:
            self.logger.error(f"从题库获取答案失败: {e}")
            return None
    
    def get_answers_from_exam_data(self, exam_id) -> Optional[Dict]:
        """从考试数据获取答案（备用方案）"""
        try:
            # 这里可以实现从其他数据源获取答案的逻辑
            # 暂时返回None，使用默认评分
            return None
        except Exception as e:
            self.logger.error(f"从考试数据获取答案失败: {e}")
            return None
    
    def auto_grade_answers(self, student_answers: Dict, correct_answers: Dict) -> Dict:
        """自动阅卷"""
        question_scores = []
        grading_details = []
        total_obtained_score = 0
        
        questions = correct_answers.get("questions", {})
        
        for question_id, correct_data in questions.items():
            student_answer = student_answers.get(question_id, "")
            correct_answer = correct_data.get("correct_answer", "")
            question_type = correct_data.get("question_type", "")
            max_score = correct_data.get("score", 10)
            
            # 根据题目类型进行评分
            obtained_score = self.grade_question(
                student_answer, correct_answer, question_type, max_score
            )
            
            question_scores.append({
                "question_id": question_id,
                "max_score": max_score,
                "obtained_score": obtained_score,
                "student_answer": student_answer,
                "correct_answer": correct_answer,
                "question_type": question_type
            })
            
            grading_details.append({
                "question_id": question_id,
                "content": correct_data.get("content", ""),
                "student_answer": student_answer,
                "correct_answer": correct_answer,
                "score": f"{obtained_score}/{max_score}",
                "is_correct": obtained_score == max_score
            })
            
            total_obtained_score += obtained_score
        
        return {
            "total_obtained_score": total_obtained_score,
            "question_scores": question_scores,
            "grading_details": grading_details
        }
    
    def grade_question(self, student_answer: Any, correct_answer: Any, 
                      question_type: str, max_score: float) -> float:
        """评分单个题目"""
        try:
            if question_type == "single_choice":
                return max_score if str(student_answer).strip() == str(correct_answer).strip() else 0
            
            elif question_type == "multiple_choice":
                # 多选题需要完全匹配
                if isinstance(student_answer, list) and isinstance(correct_answer, list):
                    student_set = set(str(x).strip() for x in student_answer)
                    correct_set = set(str(x).strip() for x in correct_answer)
                    return max_score if student_set == correct_set else 0
                else:
                    return max_score if str(student_answer).strip() == str(correct_answer).strip() else 0
            
            elif question_type == "true_false":
                # 判断题
                student_bool = str(student_answer).lower() in ['true', '1', 'yes', '是', '对', '正确']
                correct_bool = str(correct_answer).lower() in ['true', '1', 'yes', '是', '对', '正确']
                return max_score if student_bool == correct_bool else 0
            
            elif question_type == "fill_blank":
                # 填空题，简单字符串匹配
                student_text = str(student_answer).strip().lower()
                correct_text = str(correct_answer).strip().lower()
                return max_score if student_text == correct_text else 0
            
            elif question_type == "essay":
                # 简答题，暂时给一半分数（需要人工阅卷）
                if str(student_answer).strip():
                    return max_score * 0.5  # 给50%的分数
                else:
                    return 0
            
            else:
                # 未知题型，给一半分数
                return max_score * 0.5 if str(student_answer).strip() else 0
                
        except Exception as e:
            self.logger.error(f"评分题目失败: {e}")
            return 0
    
    def create_default_grading_result(self, exam_result: Dict, file_path: Path) -> bool:
        """创建默认阅卷结果（当无法获取正确答案时）"""
        try:
            answers = exam_result.get('answers', {})
            total_questions = len(answers)
            
            # 给每题10分，答题给5分，未答题给0分
            question_scores = []
            total_obtained_score = 0
            
            for i, (question_id, answer) in enumerate(answers.items(), 1):
                score = 5 if str(answer).strip() else 0
                question_scores.append({
                    "question_id": question_id,
                    "max_score": 10,
                    "obtained_score": score,
                    "student_answer": answer,
                    "correct_answer": "未知",
                    "question_type": "unknown"
                })
                total_obtained_score += score
            
            # 生成默认结果
            final_result = {
                "exam_id": exam_result.get('exam_id'),
                "user_id": exam_result.get('user_id'),
                "user_name": exam_result.get('user_name', ''),
                "username": exam_result.get('username', ''),
                "department": exam_result.get('department', ''),
                "paper_title": "默认评分试卷",
                "submit_time": exam_result.get('submit_time'),
                "grading_time": datetime.now().isoformat(),
                "total_score": total_questions * 10,
                "obtained_score": total_obtained_score,
                "final_score": total_obtained_score,
                "percentage": round((total_obtained_score / (total_questions * 10)) * 100, 2) if total_questions > 0 else 0,
                "question_scores": question_scores,
                "grading_details": [],
                "auto_graded": True,
                "grader": "default_grader",
                "note": "使用默认评分规则：答题得5分，未答题得0分"
            }
            
            # 保存结果
            graded_file = self.graded_dir / f"default_graded_{exam_result.get('exam_id')}_{exam_result.get('user_id')}_{int(time.time())}.json"
            with open(graded_file, 'w', encoding='utf-8') as f:
                json.dump(final_result, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"默认阅卷完成: {graded_file.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"创建默认阅卷结果失败: {e}")
            return False


def main():
    """主函数"""
    grader = AutoGrader()
    
    print("🎯 启动自动阅卷系统...")
    processed_count = grader.process_pending_exams()
    
    if processed_count > 0:
        print(f"✅ 成功处理 {processed_count} 个考试结果")
    else:
        print("ℹ️ 没有待处理的考试结果")


if __name__ == "__main__":
    main()
