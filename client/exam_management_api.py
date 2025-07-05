#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考试管理API集成模块
连接客户端与考试管理模块
"""

import json
import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class ExamManagementAPI:
    """考试管理API"""
    
    def __init__(self):
        self.project_root = project_root
        self.published_exams_file = self.project_root / 'exam_management' / 'published_exams.json'
        self.enrollments_file = self.project_root / 'exam_management' / 'enrollments.json'
        self.question_bank_db = self.project_root / 'question_bank_web' / 'questions.db'
    
    def get_published_exams_for_student(self, student_id=None):
        """获取学生可参加的已发布考试"""
        try:
            # 1. 获取已发布考试
            published_exams = self.load_published_exams()
            
            # 2. 如果指定了学生ID，检查学生是否被分配到考试
            if student_id:
                enrolled_exam_ids = self.get_student_enrolled_exams(student_id)
                # 过滤出学生被分配的考试
                available_exams = [
                    exam for exam in published_exams 
                    if exam.get('id') in enrolled_exam_ids
                ]
            else:
                # 如果没有指定学生ID，返回所有已发布考试
                available_exams = published_exams
            
            print(f"📋 为学生 {student_id or '未指定'} 找到 {len(available_exams)} 个可参加考试")
            return available_exams
            
        except Exception as e:
            print(f"❌ 获取已发布考试失败: {e}")
            return []
    
    def load_published_exams(self):
        """加载已发布考试列表"""
        try:
            if not self.published_exams_file.exists():
                print(f"⚠️ 已发布考试文件不存在: {self.published_exams_file}")
                return []
            
            with open(self.published_exams_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 过滤出已发布状态的考试
            published_exams = [
                exam for exam in data 
                if exam.get('status') == 'published'
            ]
            
            print(f"📋 加载了 {len(published_exams)} 个已发布考试")
            return published_exams
            
        except Exception as e:
            print(f"❌ 加载已发布考试失败: {e}")
            return []
    
    def get_student_enrolled_exams(self, student_id):
        """获取学生被分配的考试ID列表"""
        try:
            if not self.enrollments_file.exists():
                print(f"⚠️ 学生分配文件不存在: {self.enrollments_file}")
                return []
            
            with open(self.enrollments_file, 'r', encoding='utf-8') as f:
                enrollments = json.load(f)
            
            # 提取该学生被分配的考试ID
            enrolled_exam_ids = [
                enrollment.get('exam_id') 
                for enrollment in enrollments 
                if enrollment.get('student_id') == student_id
            ]
            
            print(f"📋 学生 {student_id} 被分配到 {len(enrolled_exam_ids)} 个考试")
            return enrolled_exam_ids
            
        except Exception as e:
            print(f"❌ 获取学生分配信息失败: {e}")
            return []
    
    def get_exam_details(self, exam_id):
        """获取考试详情"""
        try:
            # 1. 从已发布考试中找到考试信息
            published_exams = self.load_published_exams()
            exam_info = None
            
            for exam in published_exams:
                if exam.get('id') == exam_id:
                    exam_info = exam
                    break
            
            if not exam_info:
                print(f"❌ 未找到考试 {exam_id}")
                return None
            
            # 2. 获取考试关联的试卷ID
            paper_id = exam_info.get('paper_id')
            if not paper_id:
                print(f"❌ 考试 {exam_id} 没有关联试卷")
                return None
            
            # 3. 从题库获取试卷题目
            questions = self.get_paper_questions(paper_id)
            
            # 4. 组装考试详情
            exam_details = {
                'id': exam_id,
                'name': exam_info.get('title', '未知考试'),
                'description': exam_info.get('description', ''),
                'duration': exam_info.get('duration', 60),
                'total_score': exam_info.get('total_score', 100),
                'paper_id': paper_id,
                'questions': questions
            }
            
            print(f"✅ 获取考试详情成功: {exam_details['name']} ({len(questions)}道题)")
            return exam_details
            
        except Exception as e:
            print(f"❌ 获取考试详情失败: {e}")
            return None
    
    def get_paper_questions(self, paper_id):
        """从题库获取试卷题目"""
        try:
            import sqlite3
            
            if not self.question_bank_db.exists():
                print(f"❌ 题库数据库不存在: {self.question_bank_db}")
                return []
            
            conn = sqlite3.connect(self.question_bank_db)
            cursor = conn.cursor()
            
            # 获取试卷题目 - 修正字段名：content -> stem
            cursor.execute('''
                SELECT q.id, q.question_type_code, q.stem, q.correct_answer, pq.score
                FROM questions q
                JOIN paper_questions pq ON q.id = pq.question_id
                WHERE pq.paper_id = ?
                ORDER BY pq.question_order
            ''', (paper_id,))
            
            rows = cursor.fetchall()

            questions = []
            for row in rows:
                q_id, q_type_code, content, correct_answer, score = row

                # 获取选项 - 从题目表的选项字段构建
                options = []
                try:
                    # 查询题目的选项字段
                    cursor.execute('''
                        SELECT option_a, option_b, option_c, option_d, option_e
                        FROM questions
                        WHERE id = ?
                    ''', (q_id,))
                    option_row = cursor.fetchone()

                    if option_row:
                        for opt in option_row:
                            if opt and opt.strip():
                                options.append(opt.strip())

                except Exception as e:
                    print(f"获取题目选项失败: {e}")
                    options = []

                # 判断题特殊处理：如果选项为空，使用默认选项
                if q_type_code == 'C' and not options:  # C是判断题代码
                    options = ["正确", "错误"]
                
                # 转换题型代码
                type_mapping = {
                    'B': 'single_choice',
                    'G': 'multiple_choice', 
                    'C': 'true_false',
                    'T': 'fill_blank',
                    'D': 'short_answer',
                    'E': 'essay'
                }
                
                question_type = type_mapping.get(q_type_code, 'single_choice')
                
                questions.append({
                    'id': q_id,
                    'type': question_type,
                    'content': content,
                    'options': options,
                    'correct_answer': correct_answer,
                    'score': score
                })
            
            conn.close()
            print(f"✅ 从试卷 {paper_id} 获取到 {len(questions)} 道题目")
            return questions

        except Exception as e:
            print(f"❌ 获取试卷题目失败: {e}")
            if 'conn' in locals():
                conn.close()
            return []
    
    def get_available_exams(self, student_id=None):
        """获取可用考试列表（兼容旧API）"""
        return self.get_published_exams_for_student(student_id)

# 创建全局API实例
exam_api = ExamManagementAPI()

# 兼容函数
def get_published_exams_for_student(student_id=None):
    """获取学生可参加的已发布考试"""
    return exam_api.get_published_exams_for_student(student_id)

def get_exam_details(exam_id):
    """获取考试详情"""
    return exam_api.get_exam_details(exam_id)

def get_available_exams(student_id=None):
    """获取可用考试列表"""
    return exam_api.get_available_exams(student_id)

if __name__ == "__main__":
    # 测试API
    print("🧪 测试考试管理API")
    print("=" * 50)
    
    # 测试获取已发布考试
    exams = get_published_exams_for_student()
    print(f"📋 已发布考试: {len(exams)} 个")
    
    for exam in exams:
        print(f"  - {exam.get('title', '未知')} (ID: {exam.get('id', '未知')})")
    
    # 测试获取考试详情
    if exams:
        exam_id = exams[0].get('id')
        details = get_exam_details(exam_id)
        if details:
            print(f"✅ 考试详情: {details['name']} ({len(details['questions'])}道题)")
        else:
            print(f"❌ 获取考试详情失败")
    
    print("🎯 测试完成")
