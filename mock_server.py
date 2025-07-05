#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟服务器 - 用于测试独立客户端
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import sys

app = Flask(__name__)
CORS(app)

# 模拟用户数据
USERS = {
    "919662422786147946": {
        "id": "919662422786147946",
        "username": "919662422786147946",
        "password": "password123",
        "role": "student",
        "name": "测试考生"
    },
    "admin": {
        "id": "admin",
        "username": "admin", 
        "password": "admin123",
        "role": "admin",
        "name": "管理员"
    }
}

# 模拟考试数据
EXAMS = [
    {
        "id": "exam_001",
        "name": "计算机基础知识测试",
        "description": "测试计算机基础知识掌握情况",
        "duration": 60,
        "total_score": 100,
        "pass_score": 60,
        "question_count": 5,
        "status": "active"
    },
    {
        "id": "exam_002", 
        "name": "数学能力测试",
        "description": "测试数学基础能力",
        "duration": 90,
        "total_score": 100,
        "pass_score": 70,
        "question_count": 8,
        "status": "active"
    }
]

# 模拟题目数据
QUESTIONS = {
    "exam_001": [
        {
            "id": "q1",
            "type": "single_choice",
            "content": "以下哪个是操作系统？",
            "options": ["Windows", "Word", "Excel", "PowerPoint"]
        },
        {
            "id": "q2", 
            "type": "multiple_choice",
            "content": "以下哪些是编程语言？",
            "options": ["Python", "Java", "HTML", "CSS"]
        },
        {
            "id": "q3",
            "type": "true_false", 
            "content": "CPU是计算机的中央处理器。",
            "options": ["正确", "错误"]
        },
        {
            "id": "q4",
            "type": "fill_blank",
            "content": "计算机的三大核心组件是CPU、内存和____。"
        },
        {
            "id": "q5",
            "type": "short_answer",
            "content": "请简述什么是计算机网络？"
        }
    ],
    "exam_002": [
        {
            "id": "q1",
            "type": "single_choice", 
            "content": "2 + 3 = ?",
            "options": ["4", "5", "6", "7"]
        },
        {
            "id": "q2",
            "type": "single_choice",
            "content": "10 ÷ 2 = ?", 
            "options": ["3", "4", "5", "6"]
        },
        {
            "id": "q3",
            "type": "true_false",
            "content": "π 约等于 3.14。",
            "options": ["正确", "错误"]
        },
        {
            "id": "q4",
            "type": "fill_blank",
            "content": "一个圆的面积公式是 π × r²，其中 r 是____。"
        },
        {
            "id": "q5",
            "type": "short_answer",
            "content": "请解释什么是勾股定理？"
        },
        {
            "id": "q6",
            "type": "multiple_choice",
            "content": "以下哪些是质数？",
            "options": ["2", "3", "4", "5"]
        },
        {
            "id": "q7",
            "type": "essay",
            "content": "请详细说明如何计算一个三角形的面积，并举例说明。"
        },
        {
            "id": "q8",
            "type": "true_false",
            "content": "0 是自然数。",
            "options": ["正确", "错误"]
        }
    ]
}

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({"status": "ok", "message": "服务器运行正常"})

@app.route('/health', methods=['GET'])
def health_check_simple():
    """简单健康检查"""
    return jsonify({"status": "ok", "message": "服务器运行正常"})

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    print(f"登录请求: {username}")
    
    if username in USERS:
        user = USERS[username]
        if user['password'] == password:
            return jsonify({
                "success": True,
                "user_info": {
                    "id": user['id'],
                    "username": user['username'],
                    "role": user['role'],
                    "name": user['name']
                }
            })
    
    return jsonify({"success": False, "message": "用户名或密码错误"}), 401

@app.route('/api/exams/user/<user_id>', methods=['GET'])
def get_user_exams(user_id):
    """获取用户可参加的考试"""
    print(f"获取用户考试列表: {user_id}")
    
    # 简单模拟：所有学生都能参加所有考试
    if user_id in USERS:
        return jsonify({"exams": EXAMS})
    
    return jsonify({"exams": []}), 404

@app.route('/api/exams/<exam_id>', methods=['GET'])
def get_exam_details(exam_id):
    """获取考试详情"""
    print(f"获取考试详情: {exam_id}")
    
    # 查找考试
    exam = None
    for e in EXAMS:
        if e['id'] == exam_id:
            exam = e.copy()
            break
    
    if not exam:
        return jsonify({"error": "考试不存在"}), 404
    
    # 添加题目
    if exam_id in QUESTIONS:
        exam['questions'] = QUESTIONS[exam_id]
    else:
        exam['questions'] = []
    
    return jsonify(exam)

@app.route('/api/exams/<exam_id>/submit', methods=['POST'])
def submit_exam(exam_id):
    """提交考试答案"""
    data = request.get_json()
    user_id = data.get('user_id')
    answers = data.get('answers', {})
    submit_time = data.get('submit_time')
    
    print(f"收到答案提交: 考试={exam_id}, 用户={user_id}, 答案数量={len(answers)}")
    
    # 模拟评分
    total_questions = len(QUESTIONS.get(exam_id, []))
    answered_questions = len([a for a in answers.values() if a])
    score = int((answered_questions / total_questions) * 100) if total_questions > 0 else 0
    
    # 保存答案到文件（可选）
    try:
        answers_dir = "exam_answers"
        os.makedirs(answers_dir, exist_ok=True)
        
        answer_file = os.path.join(answers_dir, f"{exam_id}_{user_id}_{int(time.time())}.json")
        with open(answer_file, 'w', encoding='utf-8') as f:
            json.dump({
                "exam_id": exam_id,
                "user_id": user_id,
                "answers": answers,
                "submit_time": submit_time,
                "score": score
            }, f, ensure_ascii=False, indent=2)
        
        print(f"答案已保存到: {answer_file}")
    except Exception as e:
        print(f"保存答案失败: {e}")
    
    return jsonify({
        "success": True,
        "message": "答案提交成功",
        "score": score,
        "total_questions": total_questions,
        "answered_questions": answered_questions
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取服务器状态"""
    return jsonify({
        "server": "PH&RL 模拟考试服务器",
        "version": "1.0.0",
        "users": len(USERS),
        "exams": len(EXAMS),
        "status": "running"
    })

if __name__ == '__main__':
    import time
    
    print("=" * 60)
    print("🚀 PH&RL 模拟考试服务器启动")
    print("=" * 60)
    print(f"📊 用户数量: {len(USERS)}")
    print(f"📝 考试数量: {len(EXAMS)}")
    print(f"🌐 服务地址: http://127.0.0.1:5000")
    print("=" * 60)
    print("\n测试账号:")
    for username, user in USERS.items():
        print(f"  用户名: {username}")
        print(f"  密码: {user['password']}")
        print(f"  角色: {user['role']}")
        print()
    
    try:
        print("正在启动服务器...")
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"服务器启动失败: {e}")
        sys.exit(1)
