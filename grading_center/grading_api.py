#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阅卷中心API
处理考试提交、自动阅卷、成绩计算等功能
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import json
import time
import uuid
from datetime import datetime
import os
import sys

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

app = Flask(__name__)
CORS(app)

# 数据库路径
DB_PATH = os.path.join(project_root, 'grading_center', 'grading.db')

def init_database():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建考试提交表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exam_submissions (
            id TEXT PRIMARY KEY,
            exam_id TEXT NOT NULL,
            paper_id TEXT NOT NULL,
            student_id TEXT,
            student_name TEXT,
            answers TEXT NOT NULL,
            submit_time REAL NOT NULL,
            duration REAL,
            status TEXT DEFAULT 'submitted',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建阅卷结果表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grading_results (
            id TEXT PRIMARY KEY,
            submission_id TEXT NOT NULL,
            question_id TEXT NOT NULL,
            question_type TEXT,
            student_answer TEXT,
            correct_answer TEXT,
            score REAL DEFAULT 0,
            max_score REAL DEFAULT 0,
            is_correct BOOLEAN DEFAULT 0,
            grading_method TEXT DEFAULT 'auto',
            grader_id TEXT,
            grading_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            comments TEXT,
            FOREIGN KEY (submission_id) REFERENCES exam_submissions (id)
        )
    ''')
    
    # 创建成绩统计表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grade_statistics (
            id TEXT PRIMARY KEY,
            submission_id TEXT NOT NULL,
            paper_id TEXT NOT NULL,
            student_id TEXT,
            student_name TEXT,
            total_score REAL DEFAULT 0,
            max_total_score REAL DEFAULT 0,
            percentage REAL DEFAULT 0,
            grade_level TEXT,
            pass_status TEXT DEFAULT 'fail',
            grading_status TEXT DEFAULT 'pending',
            grading_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (submission_id) REFERENCES exam_submissions (id)
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """阅卷中心首页"""
    return render_template('grading_center.html')

@app.route('/api/submit_exam', methods=['POST'])
def submit_exam():
    """接收考试提交"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['exam_id', 'paper_id', 'answers', 'submit_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需字段: {field}'}), 400
        
        # 生成提交ID
        submission_id = str(uuid.uuid4())
        
        # 保存到数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO exam_submissions 
            (id, exam_id, paper_id, student_id, student_name, answers, submit_time, duration, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            submission_id,
            data['exam_id'],
            data['paper_id'],
            data.get('student_id', 'test_student'),
            data.get('student_name', '测试学生'),
            json.dumps(data['answers'], ensure_ascii=False),
            data['submit_time'],
            data.get('duration', 0),
            'submitted'
        ))
        
        conn.commit()
        conn.close()
        
        # 触发自动阅卷
        auto_grade_submission(submission_id)
        
        return jsonify({
            'success': True,
            'submission_id': submission_id,
            'message': '考试提交成功，正在进行自动阅卷'
        })
        
    except Exception as e:
        return jsonify({'error': f'提交失败: {str(e)}'}), 500

@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    """获取考试提交列表"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, g.total_score, g.max_total_score, g.percentage, g.grade_level, g.pass_status
            FROM exam_submissions s
            LEFT JOIN grade_statistics g ON s.id = g.submission_id
            ORDER BY s.submit_time DESC
        ''')
        
        submissions = []
        for row in cursor.fetchall():
            submissions.append({
                'id': row[0],
                'exam_id': row[1],
                'paper_id': row[2],
                'student_id': row[3],
                'student_name': row[4],
                'submit_time': row[6],
                'duration': row[7],
                'status': row[8],
                'total_score': row[10] if row[10] is not None else 0,
                'max_total_score': row[11] if row[11] is not None else 0,
                'percentage': row[12] if row[12] is not None else 0,
                'grade_level': row[13] if row[13] is not None else '未评分',
                'pass_status': row[14] if row[14] is not None else 'pending'
            })
        
        conn.close()
        return jsonify(submissions)
        
    except Exception as e:
        return jsonify({'error': f'获取提交列表失败: {str(e)}'}), 500

@app.route('/api/submissions/<submission_id>/details', methods=['GET'])
def get_submission_details(submission_id):
    """获取提交详情"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取提交信息
        cursor.execute('SELECT * FROM exam_submissions WHERE id = ?', (submission_id,))
        submission = cursor.fetchone()
        
        if not submission:
            return jsonify({'error': '提交不存在'}), 404
        
        # 获取阅卷结果
        cursor.execute('''
            SELECT * FROM grading_results WHERE submission_id = ? ORDER BY question_id
        ''', (submission_id,))
        grading_results = cursor.fetchall()
        
        # 获取成绩统计
        cursor.execute('SELECT * FROM grade_statistics WHERE submission_id = ?', (submission_id,))
        statistics = cursor.fetchone()
        
        conn.close()
        
        # 格式化返回数据
        result = {
            'submission': {
                'id': submission[0],
                'exam_id': submission[1],
                'paper_id': submission[2],
                'student_id': submission[3],
                'student_name': submission[4],
                'answers': json.loads(submission[5]),
                'submit_time': submission[6],
                'duration': submission[7],
                'status': submission[8]
            },
            'grading_results': [
                {
                    'id': result[0],
                    'question_id': result[2],
                    'question_type': result[3],
                    'student_answer': result[4],
                    'correct_answer': result[5],
                    'score': result[6],
                    'max_score': result[7],
                    'is_correct': bool(result[8]),
                    'grading_method': result[9],
                    'comments': result[12]
                }
                for result in grading_results
            ],
            'statistics': {
                'total_score': statistics[4] if statistics else 0,
                'max_total_score': statistics[5] if statistics else 0,
                'percentage': statistics[6] if statistics else 0,
                'grade_level': statistics[7] if statistics else '未评分',
                'pass_status': statistics[8] if statistics else 'pending'
            } if statistics else None
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'获取提交详情失败: {str(e)}'}), 500

def auto_grade_submission(submission_id):
    """自动阅卷"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取提交信息
        cursor.execute('SELECT * FROM exam_submissions WHERE id = ?', (submission_id,))
        submission = cursor.fetchone()
        
        if not submission:
            return False
        
        paper_id = submission[2]
        answers = json.loads(submission[5])
        
        # 获取试卷信息和正确答案
        question_bank_db = os.path.join(project_root, 'question_bank_web', 'questions.db')
        if os.path.exists(question_bank_db):
            qb_conn = sqlite3.connect(question_bank_db)
            qb_cursor = qb_conn.cursor()
            
            # 获取试卷题目和分数
            qb_cursor.execute('''
                SELECT q.id, q.question_type_code, q.correct_answer, pq.score
                FROM questions q
                JOIN paper_questions pq ON q.id = pq.question_id
                WHERE pq.paper_id = ?
                ORDER BY pq.question_order
            ''', (paper_id,))
            
            questions = qb_cursor.fetchall()
            qb_conn.close()
            
            total_score = 0
            max_total_score = 0
            
            # 逐题阅卷
            for question in questions:
                q_id, q_type, correct_answer, max_score = question
                student_answer = answers.get(q_id, '')
                
                # 计算得分
                score, is_correct = calculate_score(q_type, student_answer, correct_answer, max_score)
                
                # 保存阅卷结果
                cursor.execute('''
                    INSERT INTO grading_results 
                    (id, submission_id, question_id, question_type, student_answer, correct_answer, 
                     score, max_score, is_correct, grading_method)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(uuid.uuid4()),
                    submission_id,
                    q_id,
                    q_type,
                    json.dumps(student_answer, ensure_ascii=False),
                    correct_answer,
                    score,
                    max_score,
                    is_correct,
                    'auto'
                ))
                
                total_score += score
                max_total_score += max_score
            
            # 计算百分比和等级
            percentage = (total_score / max_total_score * 100) if max_total_score > 0 else 0
            grade_level = get_grade_level(percentage)
            pass_status = 'pass' if percentage >= 60 else 'fail'
            
            # 保存成绩统计
            cursor.execute('''
                INSERT INTO grade_statistics 
                (id, submission_id, paper_id, student_id, student_name, total_score, max_total_score, 
                 percentage, grade_level, pass_status, grading_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                submission_id,
                paper_id,
                submission[3],
                submission[4],
                total_score,
                max_total_score,
                percentage,
                grade_level,
                pass_status,
                'completed'
            ))
            
            # 更新提交状态
            cursor.execute('UPDATE exam_submissions SET status = ? WHERE id = ?', 
                         ('graded', submission_id))
            
            conn.commit()
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"自动阅卷失败: {e}")
        return False

def calculate_score(question_type, student_answer, correct_answer, max_score):
    """计算题目得分"""
    try:
        if question_type in ['B', 'C']:  # 单选题、判断题
            is_correct = str(student_answer).strip() == str(correct_answer).strip()
            return (max_score if is_correct else 0, is_correct)
            
        elif question_type == 'G':  # 多选题
            if isinstance(student_answer, list):
                correct_set = set(correct_answer.split(','))
                student_set = set(student_answer)
                is_correct = correct_set == student_set
                return (max_score if is_correct else 0, is_correct)
            return (0, False)
            
        elif question_type == 'T':  # 填空题
            is_correct = str(student_answer).strip() == str(correct_answer).strip()
            return (max_score if is_correct else 0, is_correct)
            
        elif question_type in ['D', 'E']:  # 简答题、论述题
            # 主观题暂时给满分，实际应用中需要人工阅卷
            if str(student_answer).strip():
                return (max_score, True)
            return (0, False)
            
        return (0, False)
        
    except Exception as e:
        print(f"计算得分失败: {e}")
        return (0, False)

def get_grade_level(percentage):
    """根据百分比获取等级"""
    if percentage >= 90:
        return 'A'
    elif percentage >= 80:
        return 'B'
    elif percentage >= 70:
        return 'C'
    elif percentage >= 60:
        return 'D'
    else:
        return 'F'

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """获取成绩统计"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 总体统计
        cursor.execute('SELECT COUNT(*) FROM exam_submissions')
        total_submissions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM grade_statistics WHERE pass_status = "pass"')
        passed_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(percentage) FROM grade_statistics')
        avg_score = cursor.fetchone()[0] or 0
        
        # 等级分布
        cursor.execute('''
            SELECT grade_level, COUNT(*) 
            FROM grade_statistics 
            GROUP BY grade_level
        ''')
        grade_distribution = dict(cursor.fetchall())
        
        conn.close()
        
        return jsonify({
            'total_submissions': total_submissions,
            'passed_count': passed_count,
            'pass_rate': (passed_count / total_submissions * 100) if total_submissions > 0 else 0,
            'average_score': round(avg_score, 2),
            'grade_distribution': grade_distribution
        })
        
    except Exception as e:
        return jsonify({'error': f'获取统计信息失败: {str(e)}'}), 500

if __name__ == '__main__':
    # 确保数据库目录存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # 初始化数据库
    init_database()
    
    print("🎯 阅卷中心API启动")
    print(f"📊 数据库路径: {DB_PATH}")
    print(f"🌐 访问地址: http://localhost:5002")
    
    app.run(host='0.0.0.0', port=5002, debug=True)
