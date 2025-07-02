#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建示例题目数据
"""

import sqlite3
import uuid
import json
from datetime import datetime

def create_sample_questions():
    """创建示例题目数据"""
    # 连接数据库
    conn = sqlite3.connect('question_bank_web/local_dev.db')
    cursor = conn.cursor()

    # 获取试卷ID
    cursor.execute('SELECT id, name FROM papers')
    papers = cursor.fetchall()

    # 为每个试卷创建题目
    for paper_id, paper_name in papers:
        print(f'为试卷 {paper_name} 创建题目...')
        
        # 创建5道示例题目
        questions = [
            {
                'id': str(uuid.uuid4()),
                'question_type_code': 'A',  # A=单选
                'question_number': f'Q001',
                'stem': f'{paper_name} - 选择题1：以下哪个选项是正确的？',
                'option_a': '选项A',
                'option_b': '选项B',
                'option_c': '选项C',
                'option_d': '选项D',
                'option_e': '',
                'image_info': '',
                'correct_answer': 'A',
                'difficulty_code': '1',  # 1=简单
                'consistency_code': '1',
                'analysis': '这是解析内容',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'question_bank_id': ''
            },
            {
                'id': str(uuid.uuid4()),
                'question_type_code': 'B',  # B=多选
                'question_number': f'Q002',
                'stem': f'{paper_name} - 多选题：以下哪些选项是正确的？（多选）',
                'option_a': '选项A',
                'option_b': '选项B',
                'option_c': '选项C',
                'option_d': '选项D',
                'option_e': '',
                'image_info': '',
                'correct_answer': 'AC',
                'difficulty_code': '2',  # 2=中等
                'consistency_code': '1',
                'analysis': '这是多选题解析',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'question_bank_id': ''
            },
            {
                'id': str(uuid.uuid4()),
                'question_type_code': 'C',  # C=判断
                'question_number': f'Q003',
                'stem': f'{paper_name} - 判断题：这个说法是正确的。',
                'option_a': '正确',
                'option_b': '错误',
                'option_c': '',
                'option_d': '',
                'option_e': '',
                'image_info': '',
                'correct_answer': 'A',
                'difficulty_code': '1',  # 1=简单
                'consistency_code': '1',
                'analysis': '这是判断题解析',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'question_bank_id': ''
            },
            {
                'id': str(uuid.uuid4()),
                'question_type_code': 'D',  # D=填空
                'question_number': f'Q004',
                'stem': f'{paper_name} - 填空题：请填写正确答案：_____',
                'option_a': '',
                'option_b': '',
                'option_c': '',
                'option_d': '',
                'option_e': '',
                'image_info': '',
                'correct_answer': '正确答案',
                'difficulty_code': '2',  # 2=中等
                'consistency_code': '1',
                'analysis': '这是填空题解析',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'question_bank_id': ''
            },
            {
                'id': str(uuid.uuid4()),
                'question_type_code': 'E',  # E=简答
                'question_number': f'Q005',
                'stem': f'{paper_name} - 简答题：请简要说明相关概念。',
                'option_a': '',
                'option_b': '',
                'option_c': '',
                'option_d': '',
                'option_e': '',
                'image_info': '',
                'correct_answer': '这是参考答案，学生应该从多个角度进行分析...',
                'difficulty_code': '3',  # 3=困难
                'consistency_code': '1',
                'analysis': '这是简答题解析',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'question_bank_id': ''
            }
        ]
        
        # 插入题目
        for i, question in enumerate(questions):
            cursor.execute('''
                INSERT OR REPLACE INTO questions
                (id, question_type_code, question_number, stem, option_a, option_b, option_c, option_d, option_e,
                 image_info, correct_answer, difficulty_code, consistency_code, analysis, created_at, updated_at, question_bank_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                question['id'], question['question_type_code'], question['question_number'],
                question['stem'], question['option_a'], question['option_b'], question['option_c'],
                question['option_d'], question['option_e'], question['image_info'],
                question['correct_answer'], question['difficulty_code'], question['consistency_code'],
                question['analysis'], question['created_at'], question['updated_at'], question['question_bank_id']
            ))
            
            # 创建试卷-题目关联
            cursor.execute('''
                INSERT OR REPLACE INTO paper_questions
                (id, paper_id, question_id, question_order, score)
                VALUES (?, ?, ?, ?, ?)
            ''', (str(uuid.uuid4()), paper_id, question['id'], i + 1, 20.0))
        
        print(f'  创建了 {len(questions)} 道题目')

    conn.commit()
    conn.close()
    print('示例题目创建完成！')

if __name__ == "__main__":
    create_sample_questions()
