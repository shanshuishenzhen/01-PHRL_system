from flask import Flask, request, render_template_string, render_template, redirect, url_for, flash, jsonify, send_file, send_from_directory, session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, joinedload
from werkzeug.utils import secure_filename
import os
import pandas as pd
from io import BytesIO
import sqlite3
import mimetypes
import re
import time
from models import Base, Question, Paper, PaperQuestion, QuestionGroup, QuestionBank
from excel_importer import import_questions_from_excel, export_error_report, export_error_report_safe
from excel_exporter import export_db_questions_to_excel
from paper_generator import PaperGenerator
import datetime
import json
from openpyxl import Workbook
from docx import Document
from json_importer import import_questions_from_json
from flask_cors import CORS

app = Flask(__name__)
# 使用固定的secret_key，避免重启后会话失效导致的错误
app.secret_key = 'phrl_question_bank_fixed_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 启用CORS
CORS(app)

# 数据库配置
# 优先使用环境变量，没有则使用SQLite作为开发数据库
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///questions.db')

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        print("Database connection successful")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"Database connection failed: {e}")
    raise

# 文件上传白名单
ALLOWED_EXTENSIONS = {'xlsx'}
ALLOWED_MIME_TYPES = {
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
}

# 文件大小限制 (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

def allowed_file(filename):
    """检查文件扩展名和MIME类型是否在允许列表中"""
    return ('.' in filename and 
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)

def cleanup_old_files():
    """清理超过24小时的上传文件"""
    upload_folder = os.path.join(os.getcwd(), 'uploads')
    if not os.path.exists(upload_folder):
        return
    
    current_time = time.time()
    for filename in os.listdir(upload_folder):
        filepath = os.path.join(upload_folder, filename)
        if os.path.isfile(filepath):
            # 检查文件是否超过24小时
            if current_time - os.path.getmtime(filepath) >24 * 3600:
                try:
                    os.remove(filepath)
                    print(f"已清理旧文件: {filename}")
                except Exception as e:
                    print(f"清理文件失败 {filename}: {e}")

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

def close_db(db):
    """关闭数据库会话"""
    if db:
        db.close()

# API路由 - 删除重复的API端点，使用下面的Bootstrap Table兼容版本

@app.route('/api/questions/<int:question_id>', methods=['GET'])
def api_get_question(question_id):
    """获取特定问题的API"""
    db = get_db()
    try:
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return jsonify({
                'status': 'error',
                'message': f'问题ID {question_id} 不存在'
            }), 404
        return jsonify({
            'status': 'success',
            'data': question.to_dict()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        close_db(db)

@app.route('/api/papers', methods=['GET'])
def api_get_papers():
    """获取所有试卷的API"""
    db = get_db()
    try:
        papers = db.query(Paper).all()
        return jsonify({
            'status': 'success',
            'data': [p.to_dict() for p in papers]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        close_db(db)

@app.route('/api/papers/<int:paper_id>', methods=['GET'])
def api_get_paper(paper_id):
    """获取特定试卷的API"""
    db = get_db()
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            return jsonify({
                'status': 'error',
                'message': f'试卷ID {paper_id} 不存在'
            }), 404
        
        # 获取试卷中的所有题目
        paper_questions = db.query(PaperQuestion).filter(PaperQuestion.paper_id == paper_id).all()
        
        # 构建包含题目详情的试卷数据
        paper_data = paper.to_dict()
        paper_data['questions'] = [pq.to_dict(include_question=True) for pq in paper_questions]
        
        return jsonify({
            'status': 'success',
            'data': paper_data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        close_db(db)

@app.route('/api/question_banks', methods=['GET'])
def api_get_question_banks():
    """获取所有题库的API"""
    db = get_db()
    try:
        question_banks = db.query(QuestionBank).all()
        return jsonify({
            'status': 'success',
            'data': [qb.to_dict() for qb in question_banks]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        close_db(db)

@app.route('/api/question_banks/<int:question_bank_id>', methods=['GET'])
def api_get_question_bank(question_bank_id):
    """获取特定题库的API"""
    db = get_db()
    try:
        question_bank = db.query(QuestionBank).filter(QuestionBank.id == question_bank_id).first()
        if not question_bank:
            return jsonify({
                'status': 'error',
                'message': f'题库ID {question_bank_id} 不存在'
            }), 404
        return jsonify({
            'status': 'success',
            'data': question_bank.to_dict()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        close_db(db)

@app.route('/api/question_groups', methods=['GET'])
def api_get_question_groups():
    """获取所有题目组的API"""
    db = get_db()
    try:
        question_groups = db.query(QuestionGroup).all()
        return jsonify({
            'status': 'success',
            'data': [qg.to_dict() for qg in question_groups]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        close_db(db)

@app.route('/api/question_groups/<int:question_group_id>', methods=['GET'])
def api_get_question_group(question_group_id):
    """获取特定题目组的API"""
    db = get_db()
    try:
        question_group = db.query(QuestionGroup).filter(QuestionGroup.id == question_group_id).first()
        if not question_group:
            return jsonify({
                'status': 'error',
                'message': f'题目组ID {question_group_id} 不存在'
            }), 404
        return jsonify({
            'status': 'success',
            'data': question_group.to_dict()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        close_db(db)

# SQL注入防护
def sanitize_input(input_str):
    """基本输入清理函数"""
    if not input_str:
        return ""
    # 移除潜在的SQL注入字符
    sanitized = re.sub(r'[;\'"\\]', '', input_str)
    return sanitized.strip()

# 题型映射字典
QUESTION_TYPE_MAP = {
    'B': {'name': '单选题', 'class': 'type-single'},
    'G': {'name': '多选题', 'class': 'type-multiple'},
    'C': {'name': '判断题', 'class': 'type-judge'},
    'T': {'name': '填空题', 'class': 'type-fill'},
    'D': {'name': '简答题', 'class': 'type-short'},
    'U': {'name': '计算题', 'class': 'type-calc'},
    'W': {'name': '论述题', 'class': 'type-essay'},
    'E': {'name': '案例分析题', 'class': 'type-case'},
    'F': {'name': '综合题', 'class': 'type-comprehensive'}
}

def get_question_type_info(type_code):
    """获取题型信息"""
    return QUESTION_TYPE_MAP.get(type_code, {'name': '未知类型', 'class': 'type-single'})

# 定义内联模板
index_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>题库管理系统</title>
    <style>body { 
            font-family: 'Microsoft YaHei', sans-serif; 
            margin: 20px; 
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #007bff;
        }
        .flashes { 
            list-style-type: none; 
            padding: 0; 
            margin-bottom: 20px;
        }
        .flashes li { 
            margin-bottom: 10px; 
            padding: 12px; 
            border-radius: 6px; 
            border-left: 4px solid;
        }
        .flashes .error { 
            background-color: #f8d7da; 
            color: #721c24; 
            border-color: #dc3545;
        }
        .flashes .success { 
            background-color: #d4edda; 
            color: #155724; 
            border-color: #28a745;
        }
        .flashes .warning { 
            background-color: #fff3cd; 
            color: #856404; 
            border-color: #ffc107;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 5px;
            transition: background-color 0.3s;
        }
        .btn:hover {
            background-color: #0056b3;
        }
        .btn-success {
            background-color: #28a745;
        }
        .btn-success:hover {
            background-color: #1e7e34;
        }
        /* 题目列表容器样式 */
        .questions-container {
            margin-top: 20px;
        }

        .questions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .question-card {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            position: relative;
        }

        .question-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transform: translateY(-2px);
        }

        .question-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }

        .question-id {
            font-family: 'Courier New', monospace;
            font-size: 12px;
            background: #f8f9fa;
            padding: 4px 8px;
            border-radius: 4px;
            color: #6c757d;
            border: 1px solid #e9ecef;
        }

        .question-type-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
            color: white;
        }

        .type-single { background: #007bff; }
        .type-multiple { background: #28a745; }
        .type-judge { background: #ffc107; color: #212529; }
        .type-fill { background: #17a2b8; }
        .type-short { background: #6f42c1; }
        .type-calc { background: #fd7e14; }
        .type-essay { background: #e83e8c; }
        .type-case { background: #20c997; }
        .type-comprehensive { background: #6c757d; }

        .question-content {
            margin-bottom: 15px;
        }

        .question-stem {
            font-size: 14px;
            line-height: 1.5;
            color: #333;
            margin-bottom: 10px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .question-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 15px;
            border-top: 1px solid #f1f3f4;
        }

        .question-difficulty {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 13px;
        }

        .difficulty-stars {
            color: #ffc107;
        }

        .question-bank-name {
            font-size: 12px;
            color: #6c757d;
            background: #f8f9fa;
            padding: 2px 8px;
            border-radius: 12px;
            border: 1px solid #e9ecef;
        }

        .question-date {
            font-size: 12px;
            color: #6c757d;
        }

        /* 表格样式保留用于其他页面 */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        tr:hover {
            background-color: #e9ecef;
        }

        /* 空状态样式 */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
            background: white;
            border-radius: 12px;
            border: 2px dashed #e9ecef;
            margin-top: 20px;
        }

        .empty-state h3 {
            margin-bottom: 10px;
            color: #495057;
        }

        .empty-state p {
            margin-bottom: 20px;
        }

        .empty-state .btn {
            margin: 0 5px;
        }
        .stats {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .stat-item {
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
        .stat-label {
            color: #6c757d;
            margin-top: 5px;
        }
        /* 分页控件样式 */
        .pagination-container {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }
        
        .pagination-info {
            text-align: center;
            margin-bottom: 15px;
            color: #6c757d;
            font-size: 14px;
        }
        
        .pagination-controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .per-page-selector {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .per-page-selector label {
            font-size: 14px;
            color: #495057;
            font-weight: 500;
        }
        
        .per-page-selector select {
            padding: 6px 12px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            background: white;
            font-size: 14px;
            cursor: pointer;
        }
        
        .per-page-selector select:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }
        
        .pagination-buttons {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }
        
        .pagination-buttons .btn {
            padding: 8px 12px;
            font-size: 14px;
            min-width: 40px;
            text-align: center;
        }
        
        .pagination-ellipsis {
            padding: 8px 12px;
            color: #6c757d;
            font-weight: bold;
        }
        
        .btn-primary {
            background: #007bff;
            color: white;
            border-color: #007bff;
        }
        
        .btn-primary:hover {
            background: #0056b3;
            border-color: #0056b3;
        }
        
        /* 题库筛选器样式 */
        .question-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }

        .question-title {
            margin: 0;
            color: #495057;
            font-size: 1.5em;
        }

        .bank-selector {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .bank-selector label {
            font-weight: 500;
            color: #495057;
            white-space: nowrap;
        }

        .bank-selector select {
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            background: white;
            font-size: 14px;
            cursor: pointer;
            min-width: 200px;
        }

        .bank-selector select:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }

        .bank-count {
            color: #6c757d;
            font-size: 0.9em;
            margin-left: 5px;
        }

        /* 视图切换器样式 */
        .view-switcher {
            display: flex;
            background: #f8f9fa;
            border-radius: 6px;
            padding: 2px;
            border: 1px solid #e9ecef;
        }

        .view-btn {
            padding: 8px 16px;
            border: none;
            background: transparent;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            color: #6c757d;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .view-btn:hover {
            background: #e9ecef;
            color: #495057;
        }

        .view-btn.active {
            background: #007bff;
            color: white;
            box-shadow: 0 2px 4px rgba(0,123,255,0.3);
        }

        .view-btn span {
            font-size: 16px;
        }

        /* 表格视图样式 */
        .table-view {
            display: none;
            margin-top: 20px;
        }

        .table-view.active {
            display: block;
        }

        .table-view table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .table-view th {
            background: #f8f9fa;
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #e9ecef;
        }

        .table-view td {
            padding: 12px;
            border-bottom: 1px solid #f1f3f4;
            vertical-align: top;
        }

        .table-view tr:hover {
            background: #f8f9fa;
        }

        .table-view .question-id-cell {
            font-family: 'Courier New', monospace;
            font-size: 12px;
            background: #f8f9fa;
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
        }

        .table-view .question-stem-cell {
            max-width: 300px;
            line-height: 1.4;
        }

        .table-view .type-badge-small {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
            color: white;
            display: inline-block;
        }

        /* 响应式设计 */
        @media (max-width: 768px) {
            .pagination-controls {
                flex-direction: column;
                align-items: center;
            }

            .pagination-buttons {
                justify-content: center;
            }

            .pagination-buttons .btn {
                padding: 6px 10px;
                font-size: 13px;
                min-width: 35px;
            }

            .question-header {
                flex-direction: column;
                gap: 15px;
                align-items: stretch;
            }

            .question-header > div:last-child {
                flex-direction: column;
                gap: 15px;
                align-items: stretch;
            }

            .view-switcher {
                justify-content: center;
            }

            .view-btn {
                flex: 1;
                justify-content: center;
            }

            .bank-selector {
                justify-content: center;
            }

            .bank-selector select {
                min-width: 100%;
            }

            /* 题目卡片响应式 */
            .questions-grid {
                grid-template-columns: 1fr;
                gap: 15px;
            }

            .question-card {
                padding: 15px;
            }

            .question-header {
                flex-direction: column;
                gap: 10px;
                align-items: flex-start;
            }

            .question-id {
                font-size: 11px;
                padding: 3px 6px;
            }

            .question-type-badge {
                font-size: 11px;
                padding: 3px 10px;
            }

            .question-stem {
                font-size: 13px;
                -webkit-line-clamp: 4;
            }

            .question-meta {
                flex-direction: column;
                gap: 10px;
                align-items: flex-start;
            }

            .question-meta > div:last-child {
                align-self: flex-end;
            }
        }

        @media (max-width: 480px) {
            .questions-grid {
                gap: 10px;
            }

            .question-card {
                padding: 12px;
            }

            .question-stem {
                font-size: 12px;
                -webkit-line-clamp: 3;
            }

            .question-difficulty {
                font-size: 12px;
            }

            .question-bank-name,
            .question-date {
                font-size: 11px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>题库管理系统</h1>
            <p>专业的题库导入和管理平台</p>
        </div>

        
        <div style="text-align: center; margin-bottom: 20px;">
            <a href="{{ url_for('handle_import_excel') }}" class="btn btn-success">导入Excel题库</a>
            <a href="{{ url_for('handle_import_sample') }}" class="btn btn-primary">导入样例题库</a>
            <a href="{{ url_for('download_template') }}" class="btn">下载题库模板</a>
            <a href="{{ url_for('index') }}" class="btn">刷新页面</a>
            <a href="{{ url_for('handle_export_excel') }}" class="btn btn-success">导出题库</a>
            <a href="/browse" class="btn btn-warning">高级浏览</a>
            <a href="/quick-generate" class="btn btn-primary">快速生成</a>
            <a href="/generate-paper" class="btn btn-warning">自定义组题</a>
            <a href="/upload-paper-rule" class="btn btn-danger">上传组题规则</a>
            <a href="/banks" class="btn btn-info">题库管理</a>
        </div>{% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <ul class=flashes>{% for category, message in messages %}
          <li class="{{ category }}">{{ message }}</li>{% endfor %}
        </ul>{% endif %}
    {% endwith %}

        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{{ questions|length }}</div>
                <div class="stat-label">当前页题目数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{{ filtered_total if selected_bank_id else total_questions }}</div>
                <div class="stat-label">{% if selected_bank_id %}筛选题目数{% else %}总题目数{% endif %}</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{{ total_banks }}</div>
                <div class="stat-label">题库数量</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{{ total_pages }}</div>
                <div class="stat-label">总页数</div>
            </div>
        </div>

        <!-- 题目列表标题和控制器 -->
        <div class="question-header">
            <h2 class="question-title">题目列表 (第 {{ current_page }}/{{ total_pages }} 页，每页 {{ per_page }} 条)</h2>
            <div style="display: flex; align-items: center; gap: 20px;">
                <!-- 视图切换器 -->
                <div class="view-switcher">
                    <button id="card-view-btn" class="view-btn active" onclick="switchView('card')">
                        <span>📋</span> 卡片视图
                    </button>
                    <button id="table-view-btn" class="view-btn" onclick="switchView('table')">
                        <span>📊</span> 表格视图
                    </button>
                </div>

                <!-- 题库选择器 -->
                <div class="bank-selector">
                    <label for="bank-select">选择题库：</label>
                    <select id="bank-select" onchange="filterByBank(this.value)">
                        <option value="">全部题库 ({{ total_questions }})</option>
                        {% for bank in banks_with_count %}
                        <option value="{{ bank.id }}" {% if selected_bank_id == bank.id %}selected{% endif %}>
                            {{ bank.name }} ({{ bank.question_count }})
                        </option>
                        {% endfor %}
                    </select>
                </div>
            </div>
        </div>

        <!-- 题目列表容器 -->
        <div class="questions-container">{% if questions %}
            <!-- 卡片视图 -->
            <div id="card-view" class="questions-grid">{% for q in questions %}
                <div class="question-card">
                    <div class="question-header">
                        <div class="question-id">{{ q.id.split('#')[0] if '#' in q.id else q.id }}</div>
                        <div class="question-type-badge {{ get_question_type_info(q.question_type_code)['class'] }}">
                            {{ get_question_type_info(q.question_type_code)['name'] }}
                        </div>
                    </div>

                    <div class="question-content">
                        <div class="question-stem">{{ q.stem }}</div>
                    </div>

                    <div class="question-meta">
                        <div class="question-difficulty">
                            <span class="difficulty-stars">
                                {% if q.difficulty_code == '1（很简单）' %}⭐
                                {% elif q.difficulty_code == '2（简单）' %}⭐⭐
                                {% elif q.difficulty_code == '3（中等）' %}⭐⭐⭐
                                {% elif q.difficulty_code == '4（困难）' %}⭐⭐⭐⭐
                                {% elif q.difficulty_code == '5（很难）' %}⭐⭐⭐⭐⭐
                                {% else %}⭐⭐⭐{% endif %}
                            </span>
                            <span>
                                {% if q.difficulty_code == '1（很简单）' %}很简单
                                {% elif q.difficulty_code == '2（简单）' %}简单
                                {% elif q.difficulty_code == '3（中等）' %}中等
                                {% elif q.difficulty_code == '4（困难）' %}困难
                                {% elif q.difficulty_code == '5（很难）' %}很难
                                {% else %}中等{% endif %}
                            </span>
                        </div>

                        <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 5px;">
                            <div class="question-bank-name">
                                {% if q.question_bank is not none %}{{ q.question_bank.name }}{% else %}未指定{% endif %}
                            </div>
                            <div class="question-date">
                                {{ q.created_at.strftime('%Y-%m-%d %H:%M') if q.created_at else 'N/A' }}
                            </div>
                        </div>
                    </div>
                </div>{% endfor %}
            </div>

            <!-- 表格视图 -->
            <div id="table-view" class="table-view">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>题库名称</th>
                            <th>题干</th>
                            <th>题型</th>
                            <th>难度</th>
                            <th>创建时间</th>
                        </tr>
                    </thead>
                    <tbody>{% for q in questions %}
                        <tr>
                            <td><span class="question-id-cell">{{ q.id.split('#')[0] if '#' in q.id else q.id }}</span></td>
                            <td>{% if q.question_bank is not none %}{{ q.question_bank.name }}{% else %}未指定{% endif %}</td>
                            <td class="question-stem-cell">{{ q.stem | truncate(100) }}</td>
                            <td>
                                <span class="type-badge-small {{ get_question_type_info(q.question_type_code)['class'] }}">
                                    {{ get_question_type_info(q.question_type_code)['name'] }}
                                </span>
                            </td>
                            <td>
                                <span style="color: #ffc107;">
                                    {% if q.difficulty_code == '1（很简单）' %}⭐
                                    {% elif q.difficulty_code == '2（简单）' %}⭐⭐
                                    {% elif q.difficulty_code == '3（中等）' %}⭐⭐⭐
                                    {% elif q.difficulty_code == '4（困难）' %}⭐⭐⭐⭐
                                    {% elif q.difficulty_code == '5（很难）' %}⭐⭐⭐⭐⭐
                                    {% else %}⭐⭐⭐{% endif %}
                                </span>
                                {% if q.difficulty_code == '1（很简单）' %}很简单
                                {% elif q.difficulty_code == '2（简单）' %}简单
                                {% elif q.difficulty_code == '3（中等）' %}中等
                                {% elif q.difficulty_code == '4（困难）' %}困难
                                {% elif q.difficulty_code == '5（很难）' %}很难
                                {% else %}中等{% endif %}
                            </td>
                            <td>{{ q.created_at.strftime('%Y-%m-%d %H:%M') if q.created_at else 'N/A' }}</td>
                        </tr>{% endfor %}
                    </tbody>
                </table>
            </div>{% else %}
            <div class="empty-state">
                <h3>暂无题目</h3>
                <p>{% if selected_bank_id %}当前题库中还没有任何题目{% else %}数据库中还没有任何题目{% endif %}，请通过以下方式添加：</p>
                <a href="{{ url_for('import_excel') }}" class="btn btn-primary">导入Excel题库</a>
                <a href="{{ url_for('import_sample') }}" class="btn btn-success">导入样例题库</a>
            </div>{% endif %}
        </div>

    <!-- 分页控件 -->{% if total_pages >1 %}
    <div class="pagination-container">
        <div class="pagination-info">显示第 {{ (current_page-1) * per_page + 1 }} - {{ [current_page * per_page, filtered_total if selected_bank_id else total_questions] | min }} 条，共 {{ filtered_total if selected_bank_id else total_questions }} 条记录
        </div>

        <div class="pagination-controls">
            <div class="per-page-selector">
                <label for="per-page">每页显示：</label>
                <select id="per-page" onchange="changePerPage(this.value)">
                    <option value="15" {% if per_page == 15 %}selected{% endif %}>15</option>
                    <option value="30" {% if per_page == 30 %}selected{% endif %}>30</option>
                    <option value="50" {% if per_page == 50 %}selected{% endif %}>50</option>
                    <option value="100" {% if per_page == 100 %}selected{% endif %}>100</option>
                </select>
            </div>

            <div class="pagination-buttons">
                <!-- 首页 -->{% if current_page >1 %}
                <a href="?page=1&per_page={{ per_page }}{% if selected_bank_id %}&bank_id={{ selected_bank_id }}{% endif %}" class="btn btn-outline-primary">首页</a>{% endif %}

                <!-- 上一页 -->{% if current_page >1 %}
                <a href="?page={{ current_page - 1 }}&per_page={{ per_page }}{% if selected_bank_id %}&bank_id={{ selected_bank_id }}{% endif %}" class="btn btn-outline-primary">上一页</a>{% endif %}

                <!-- 页码 -->{% set start_page = [1, current_page - 2] | max %}
                {% set end_page = [total_pages, current_page + 2] | min %}

                {% if start_page >1 %}
                <a href="?page=1&per_page={{ per_page }}{% if selected_bank_id %}&bank_id={{ selected_bank_id }}{% endif %}" class="btn btn-outline-secondary">1</a>{% if start_page >2 %}
                <span class="pagination-ellipsis">...</span>{% endif %}
                {% endif %}

                {% for page_num in range(start_page, end_page + 1) %}
                {% if page_num == current_page %}
                <span class="btn btn-primary">{{ page_num }}</span>{% else %}
                <a href="?page={{ page_num }}&per_page={{ per_page }}{% if selected_bank_id %}&bank_id={{ selected_bank_id }}{% endif %}" class="btn btn-outline-secondary">{{ page_num }}</a>{% endif %}
                {% endfor %}

                {% if end_page < total_pages %}
                {% if end_page < total_pages - 1 %}
                <span class="pagination-ellipsis">...</span>{% endif %}
                <a href="?page={{ total_pages }}&per_page={{ per_page }}{% if selected_bank_id %}&bank_id={{ selected_bank_id }}{% endif %}" class="btn btn-outline-secondary">{{ total_pages }}</a>{% endif %}

                <!-- 下一页 -->{% if current_page < total_pages %}
                <a href="?page={{ current_page + 1 }}&per_page={{ per_page }}{% if selected_bank_id %}&bank_id={{ selected_bank_id }}{% endif %}" class="btn btn-outline-primary">下一页</a>{% endif %}

                <!-- 末页 -->{% if current_page < total_pages %}
                <a href="?page={{ total_pages }}&per_page={{ per_page }}{% if selected_bank_id %}&bank_id={{ selected_bank_id }}{% endif %}" class="btn btn-outline-primary">末页</a>{% endif %}
            </div>
        </div>
    </div>{% endif %}

    <!-- 分页、筛选和视图切换功能 -->
    <script>
        function changePerPage(value) {
            const url = new URL(window.location);
            url.searchParams.set('per_page', value);
            url.searchParams.set('page', '1'); // 重置到第一页
            window.location.href = url.toString();
        }

        function filterByBank(bankId) {
            const url = new URL(window.location);
            if (bankId) {
                url.searchParams.set('bank_id', bankId);
            } else {
                url.searchParams.delete('bank_id');
            }
            url.searchParams.set('page', '1'); // 重置到第一页
            window.location.href = url.toString();
        }

        function switchView(viewType) {
            const cardView = document.getElementById('card-view');
            const tableView = document.getElementById('table-view');
            const cardBtn = document.getElementById('card-view-btn');
            const tableBtn = document.getElementById('table-view-btn');

            if (viewType === 'card') {
                cardView.style.display = 'grid';
                tableView.style.display = 'none';
                cardBtn.classList.add('active');
                tableBtn.classList.remove('active');
                localStorage.setItem('preferredView', 'card');
            } else {
                cardView.style.display = 'none';
                tableView.style.display = 'block';
                cardBtn.classList.remove('active');
                tableBtn.classList.add('active');
                localStorage.setItem('preferredView', 'table');
            }
        }

        // 页面加载时恢复用户偏好的视图
        document.addEventListener('DOMContentLoaded', function() {
            const preferredView = localStorage.getItem('preferredView') || 'card';
            switchView(preferredView);
        });
        
        // 键盘快捷键支持
        document.addEventListener('keydown', function(e) {
            // 左箭头键 - 上一页
            if (e.key === 'ArrowLeft' && !e.ctrlKey && !e.altKey) {
                const prevBtn = document.querySelector('a[href*="page={{ current_page-1 }}"]');
                if (prevBtn) {
                    e.preventDefault();
                    window.location.href = prevBtn.href;
                }
            }
            // 右箭头键 - 下一页
            else if (e.key === 'ArrowRight' && !e.ctrlKey && !e.altKey) {
                const nextBtn = document.querySelector('a[href*="page={{ current_page+1 }}"]');
                if (nextBtn) {
                    e.preventDefault();
                    window.location.href = nextBtn.href;
                }
            }
            // Home键 - 首页
            else if (e.key === 'Home' && !e.ctrlKey && !e.altKey) {
                const firstBtn = document.querySelector('a[href*="page=1"]');
                if (firstBtn) {
                    e.preventDefault();
                    window.location.href = firstBtn.href;
                }
            }
            // End键 - 末页
            else if (e.key === 'End' && !e.ctrlKey && !e.altKey) {
                const lastBtn = document.querySelector('a[href*="page={{ total_pages }}"]');
                if (lastBtn) {
                    e.preventDefault();
                    window.location.href = lastBtn.href;
                }
            }
        });
    </script>
</body>
</html>"""

import_form_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>导入Excel题库</title>
    <style>body { 
            font-family: 'Microsoft YaHei', sans-serif; 
            margin: 20px; 
            background-color: #f5f5f5;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #007bff;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #333;
        }
        input[type="file"] {
            width: 100%;
            padding: 10px;
            border: 2px dashed #ddd;
            border-radius: 5px;
            background: #f8f9fa;
        }
        input[type="submit"] {
            width: 100%;
            padding: 12px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        input[type="submit"]:hover {
            background-color: #0056b3;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background-color: #6c757d;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 20px;
            transition: background-color 0.3s;
        }
        .btn:hover {
            background-color: #545b62;
        }
        .info {
            background: #e7f3ff;
            border: 1px solid #b3d9ff;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .info h4 {
            margin-top: 0;
            color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>导入Excel题库</h1>
            <p>请选择要导入的Excel文件</p>
        </div>
        
        <div class="info">
            <h4>文件要求：</h4>
            <ul>
                <li>文件格式：.xlsx (Excel 2007及以上版本)</li>
                <li>文件大小：不超过10MB</li>
                <li>必需列：ID, 题库名称, 题型代码, 试题（题干）, 正确答案, 难度代码</li>
            </ul>
            <p style="margin-top: 15px;">
                <strong>提示：</strong>如果您不确定Excel文件格式，请先 
                <a href="{{ url_for('download_template') }}" style="color: #007bff; text-decoration: underline;">下载题库模板</a>作为参考。
            </p>
        </div>
        
    <form method="post" enctype="multipart/form-data" action="{{ url_for('handle_import_excel') }}">
            <div class="form-group">
                <label for="file">选择Excel文件 (.xlsx):</label>
                <input type="file" id="file" name="file" accept=".xlsx" required>
            </div>
            <input type="submit" value=" 上传并导入">
    </form>
        
        <div style="text-align: center;">
            <a href="{{ url_for('index') }}" class="btn">← 返回首页</a>
        </div>
    </div>
</body>
</html>"""

banks_template = """
<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><title>题库管理</title></head>
<body>
    <h1>题库管理</h1>
    <a href="{{ url_for('index') }}">返回首页</a>
    <h2>新增题库</h2>
    <form method="post" action="{{ url_for('manage_banks') }}">
        <input type="text" name="bank_name" required placeholder="输入新题库名称">
        <button type="submit">创建</button>
    </form>
    <h2>现有题库</h2>{% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <ul>{% for c, m in messages %}<li class="{{ c }}">{{ m|safe }}</li>{% endfor %}</ul>{% endif %}
    {% endwith %}
    {% if banks %}
        <table border="1">
            <tr><th>题库名称</th><th>创建时间</th><th>操作</th></tr>{% for bank in banks %}
            <tr>
                <td>{{ bank.name }}</td>
                <td>{{ bank.created_at.strftime('%Y-%m-%d %H:%M') if bank.created_at }}</td>
                <td>
                    <form method="post" action="{{ url_for('delete_bank', bank_id=bank.id) }}" style="display:inline;" onsubmit="return confirm('确定要删除该题库吗？此操作会同时删除该题库下所有题目！');">
                        <button type="submit">删除</button>
                    </form>
                </td>
            </tr>{% endfor %}
        </table>{% else %}
        <p>暂无题库。</p>{% endif %}
</body></html>"""

@app.route('/api/questions')
def api_questions():
    """API 端点：根据筛选条件返回题目列表。"""
    # 获取查询参数
    ids = request.args.get('ids')
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 15))
    sort_by = request.args.get('sort')
    sort_order = request.args.get('order', 'asc')
    
    q_type = request.args.get('type')
    search_term = request.args.get('search')
    
    db_session = None
    try:
        db_session = get_db()
        query = db_session.query(Question)
        
        # 如果提供了ids参数，按ID列表筛选
        if ids:
            id_list = ids.split(',')
            query = query.filter(Question.id.in_(id_list))
        
        # 应用其他筛选条件
        if q_type:
            query = query.filter(Question.question_type_code == q_type)

        if search_term:
            search_term = f"%{search_term}%"
            query = query.filter(Question.stem.like(search_term) | Question.id.like(search_term))

        # 支持知识点筛选
        knowledge_point_l1 = request.args.get('knowledge_point_l1')
        knowledge_point_l2 = request.args.get('knowledge_point_l2')
        knowledge_point_l3 = request.args.get('knowledge_point_l3')

        if knowledge_point_l3:
            query = query.filter(Question.id.like(f"%{knowledge_point_l3}%"))
        elif knowledge_point_l2:
            query = query.filter(Question.id.like(f"%{knowledge_point_l2}%"))
        elif knowledge_point_l1:
            query = query.filter(Question.id.like(f"%{knowledge_point_l1}%"))
        
        # 应用排序
        if sort_by:
            column = getattr(Question, sort_by, Question.id)
            if sort_order == 'desc':
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
        else:
            # 默认按ID排序
            query = query.order_by(Question.id.asc())
        
        # 获取总数
        total = query.count()
        
        # 应用分页
        questions = query.offset(offset).limit(limit).all()
        
        # 转换为Bootstrap Table兼容的JSON格式
        questions_data = []
        for q in questions:
            q_dict = q.to_dict()
            # 添加题型名称映射
            type_names = {
                'B': '单选题',
                'G': '多选题',
                'C': '判断题',
                'T': '填空题',
                'D': '简答题',
                'U': '计算题',
                'W': '论述题',
                'E': '案例分析题',
                'F': '综合题'
            }
            q_dict['type_name'] = type_names.get(q.question_type_code, q.question_type_code)

            # 添加知识点信息（从ID中提取）
            if q.id and '-' in q.id:
                parts = q.id.split('-')
                if len(parts) >= 3:
                    q_dict['knowledge_point_l1'] = parts[1] if len(parts) >1 else ''
                    q_dict['knowledge_point_l2'] = f"{parts[1]}-{parts[2]}" if len(parts) >2 else ''
                    q_dict['knowledge_point_l3'] = f"{parts[1]}-{parts[2]}-{parts[3]}" if len(parts) >3 else ''

            questions_data.append(q_dict)

        result = {
            'total': total,
            'rows': questions_data
        }

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        close_db(db_session)

@app.route('/api/knowledge-tree')
def api_knowledge_tree():
    """API 端点：返回知识点树结构"""
    db_session = None
    try:
        db_session = get_db()

        # 获取所有题目的ID，从中提取知识点结构
        questions = db_session.query(Question.id).all()

        tree = {}
        for question in questions:
            if question.id and '-' in question.id:
                parts = question.id.split('-')
                if len(parts) >= 4:  # 至少要有 B-A-01-001 这样的格式
                    l1 = parts[1]
                    l2 = f"{parts[1]}-{parts[2]}"
                    l3 = f"{parts[1]}-{parts[2]}-{parts[3]}"

                    if l1 not in tree:
                        tree[l1] = {}
                    if l2 not in tree[l1]:
                        tree[l1][l2] = []
                    if l3 not in tree[l1][l2]:
                        tree[l1][l2].append(l3)

        return jsonify(tree)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        close_db(db_session)

@app.route('/api/question-types')
def api_question_types():
    """API 端点：返回所有题型"""
    db_session = None
    try:
        db_session = get_db()

        # 获取所有不同的题型
        types = db_session.query(Question.question_type_code).distinct().all()

        type_names = {
            'B': '单选题',
            'G': '多选题',
            'C': '判断题',
            'T': '填空题',
            'D': '简答题',
            'U': '计算题',
            'W': '论述题',
            'E': '案例分析题',
            'F': '综合题'
        }

        result = []
        for type_row in types:
            type_code = type_row[0]
            if type_code:
                result.append({
                    'code': type_code,
                    'name': type_names.get(type_code, type_code)
                })

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        close_db(db_session)

@app.route('/api/questions/<question_id>')
def api_question_detail(question_id):
    """API 端点：返回单个题目的详细信息。"""
    db_session = None
    try:
        db_session = get_db()
        question = db_session.query(Question).filter(Question.id == question_id).first()
        
        if question:
            return jsonify(question.to_dict())
        else:
            return jsonify({'error': f'题目 {question_id} 不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        close_db(db_session)

@app.route('/')
def index():
    """主页，显示题库统计和题目列表（支持分页和题库筛选）"""
    db = get_db()
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 15))
        selected_bank_id = request.args.get('bank_id', '')

        # 确保参数有效
        if page < 1:
            page = 1
        if per_page < 1 or per_page >100:
            per_page = 15

        # 获取统计信息
        total_questions = db.query(Question).count()
        total_papers = db.query(Paper).count()
        total_banks = db.query(QuestionBank).count()

        # 获取题库列表及其题目数量
        banks_with_count = []
        banks = db.query(QuestionBank).all()
        for bank in banks:
            question_count = db.query(Question).filter(Question.question_bank_id == bank.id).count()
            banks_with_count.append({
                'id': bank.id,
                'name': bank.name,
                'question_count': question_count
            })

        # 构建查询条件
        query = db.query(Question)
        if selected_bank_id:
            query = query.filter(Question.question_bank_id == selected_bank_id)
            # 重新计算筛选后的总数
            filtered_total = query.count()
        else:
            filtered_total = total_questions

        # 计算分页信息
        total_pages = (filtered_total + per_page - 1) // per_page if filtered_total >0 else 1
        offset = (page - 1) * per_page

        # 获取当前页的题目
        questions = query.order_by(Question.id.desc()).offset(offset).limit(per_page).all()

        return render_template_string(
            index_template,
            total_questions=total_questions,
            filtered_total=filtered_total,
            total_papers=total_papers,
            total_banks=total_banks,
            banks=banks,
            banks_with_count=banks_with_count,
            questions=questions,
            current_page=page,
            total_pages=total_pages,
            per_page=per_page,
            selected_bank_id=selected_bank_id,
            get_question_type_info=get_question_type_info
        )
    finally:
        close_db(db)

@app.route('/browse')
def browse():
    """Bootstrap Table浏览页面"""
    return render_template('index.html')

@app.route('/import-json', methods=['GET'])
def handle_import_json():
    """处理从JSON文件导入样例题库的请求"""
    db = get_db()
    json_file_path = os.path.join(os.path.dirname(__file__), 'questions_sample.json')
    
    if not os.path.exists(json_file_path):
        flash(f"错误：样例题库文件 'questions_sample.json' 不存在。", 'error')
        return redirect(url_for('index'))
    
    try:
        success_count, fail_count = import_questions_from_json(json_file_path, db)
        if success_count >0:
            flash(f"成功导入 {success_count} 道新的样例题目！", 'success')
        else:
            flash("没有新的样例题目需要导入，或所有题目ID已存在。", 'warning')
        if fail_count >0:
            flash(f"有 {fail_count} 道题目导入失败，请检查服务器日志。", 'error')

    except Exception as e:
        flash(f"导入过程中发生未知错误: {e}", 'error')
    finally:
        close_db(db)
        
    return redirect(url_for('index'))

@app.route('/import-sample', methods=['GET'])
def handle_import_sample():
    """处理从Excel文件导入样例题库的请求"""
    current_project = session.get('current_project', 'default')
    print(f"当前项目: {current_project}")
    
    db = get_db()
    excel_file_path = os.path.join(os.path.dirname(__file__), 'questions_sample.xlsx')
    
    if not os.path.exists(excel_file_path):
        flash(f"错误：样例题库文件 'questions_sample.xlsx' 不存在。", 'error')
        return redirect(url_for('index'))
    
    try:
        print(f"开始导入样例题库到项目: {current_project}")
        questions_added, errors = import_questions_from_excel(excel_file_path, db)
        print(f"导入完成: 添加 {len(questions_added) if questions_added else 0} 个题目, {len(errors) if errors else 0} 个错误")
        
        if errors:
            # 使用更安全的错误报告生成方式
            try:
                error_report_path = export_error_report_safe(errors, "sample_import_errors.txt")
                if error_report_path and os.path.exists(error_report_path):
                    error_link = f'<a href="/download_error_report/{os.path.basename(error_report_path)}" target="_blank">点击查看报告</a>'
                    if questions_added:
                        flash(f'成功导入 {len(questions_added)} 条样例题目，但有部分数据出错。{error_link}', 'warning')
                    else:
                        flash(f'导入失败，所有样例题目均有问题。{error_link}', 'error')
                else:
                    # 如果错误报告生成失败，仍然显示基本信息
                    if questions_added:
                        flash(f'成功导入 {len(questions_added)} 条样例题目，但有部分数据出错。错误报告生成失败。', 'warning')
                    else:
                        flash(f'导入失败，所有样例题目均有问题。错误报告生成失败。', 'error')
            except Exception as report_error:
                print(f"错误报告生成异常: {report_error}")
                # 即使错误报告生成失败，也要显示导入结果
                if questions_added:
                    flash(f'成功导入 {len(questions_added)} 条样例题目，但有部分数据出错。', 'warning')
                else:
                    flash(f'导入失败，所有样例题目均有问题。', 'error')
        elif questions_added:
            flash(f'成功导入 {len(questions_added)} 条样例题目！', 'success')
        else:
            flash('未在样例题库中找到可导入的新题目。', 'info')
            
    except Exception as e:
        print(f"导入异常详情: {traceback.format_exc()}")
        flash(f"导入过程中发生未知错误: {e}", 'error')
    finally:
        close_db(db)
        
    return redirect(url_for('index'))

@app.route('/import-excel', methods=['GET', 'POST'])
def handle_import_excel():
    """处理Excel导入"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('没有文件部分', 'error')
            return redirect(request.url)
        file = request.files['file']
        if not file or not file.filename:
            flash('未选择文件', 'warning')
            return redirect(request.url)
        
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            db_session = get_db()
            try:
                file.save(filepath)
                # 现在这个函数会直接处理数据库提交
                questions_added, errors = import_questions_from_excel(filepath, db_session)
                
                if errors:
                    error_report_path = export_error_report_safe(errors, filename)
                    error_link = f'<a href="/download_error_report/{os.path.basename(error_report_path)}" target="_blank">点击查看报告</a>'
                    if questions_added:
                        flash(f'成功导入 {len(questions_added)} 条题目，但有部分数据出错。{error_link}', 'warning')
                    else:
                        flash(f'导入失败，所有条目均有问题。{error_link}', 'error')

                elif questions_added:
                    flash(f'成功导入 {len(questions_added)} 条题目！', 'success')
                else:
                    flash('未在文件中找到可导入的新题目。', 'info')
                
            except Exception as e:
                # 现在的导入函数会自己回滚，这里主要捕获文件保存等其他错误
                flash(f'处理文件时发生严重错误: {e}', 'error')
            finally:
                close_db(db_session)
            
            return redirect(url_for('index'))

    return render_template_string(import_form_template)

@app.route('/download-template', methods=['GET'])
def download_template():
    """下载题库模板"""
    try:
        # 检查模板文件是否存在
        template_path = os.path.join(os.getcwd(), 'templates', '题库模板.xlsx')
        
        if not os.path.exists(template_path):
            # 如果模板文件不存在，则生成一个
            from create_template import create_question_bank_template
            template_path = create_question_bank_template()
        
        # 返回文件
        return send_file(
            template_path,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='题库模板.xlsx'
        )
        
    except Exception as e:
        flash(f'下载模板文件失败: {e}', 'error')
        return redirect(url_for('index'))

@app.route('/download_error_report/<filename>')
def download_error_report(filename):
    """下载错误报告"""
    if not filename:
        flash("无效的文件名。", "error")
        return redirect(url_for('index'))
    try:
        # 安全地构建文件路径
        safe_filename = secure_filename(filename)
        # 假设 UPLOAD_FOLDER 是错误报告存储的地方
        return send_from_directory(app.config['UPLOAD_FOLDER'], safe_filename, as_attachment=True)
    except FileNotFoundError:
        flash("错误报告文件未找到。", "error")
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"下载错误报告失败: {e}", "error")
        return redirect(url_for('index'))

# 组题功能路由
@app.route('/papers')
def papers():
    """试卷列表页面"""
    db_session = None
    papers_list = []
    
    try:
        db_session = get_db()
        papers_list = db_session.query(Paper).order_by(Paper.created_at.desc()).all()
    except Exception as e:
        flash(f"获取试卷列表失败: {e}", "error")
    finally:
        close_db(db_session)
    
    return render_template_string(papers_template, papers=papers_list)

@app.route('/generate-paper', methods=['GET', 'POST'])
def generate_paper():
    """生成试卷页面"""
    if request.method == 'POST':
        try:
            db_session = get_db()
            generator = PaperGenerator(db_session)
            
            # 获取表单数据
            paper_name = request.form.get('paper_name', '').strip()
            paper_description = request.form.get('paper_description', '').strip()
            total_score = float(request.form.get('total_score', 100))
            duration = int(request.form.get('duration', 120))
            difficulty_level = request.form.get('difficulty_level', '中等')
            
            # 验证必填字段
            if not paper_name:
                flash("试卷名称不能为空", "error")
                return redirect(url_for('generate_paper'))
            
            # 获取组题规则
            rules = []
            rule_count = int(request.form.get('rule_count', 0))
            
            for i in range(rule_count):
                question_type = request.form.get(f'rule_{i}_type')
                difficulty = request.form.get(f'rule_{i}_difficulty')
                count = int(request.form.get(f'rule_{i}_count', 1))
                score = float(request.form.get(f'rule_{i}_score', 5.0))
                section_name = request.form.get(f'rule_{i}_section', '')
                
                if question_type and difficulty and count >0:
                    rules.append({
                        'question_type': question_type,
                        'difficulty': difficulty,
                        'count': count,
                        'score_per_question': score,
                        'section_name': section_name
                    })
            
            # 生成试卷
            if rules:
                paper = generator.generate_paper_by_rules(
                    paper_name=paper_name,
                    paper_description=paper_description,
                    total_score=total_score,
                    duration=duration,
                    difficulty_level=difficulty_level,
                    rules=rules
                )
                flash(f"试卷 '{paper.name}' 生成成功！", "success")
                return redirect(url_for('view_paper', paper_id=paper.id))
            else:
                flash("请至少添加一条组题规则", "error")
                
        except ValueError as e:
            flash(f"参数错误: {e}", "error")
        except Exception as e:
            flash(f"生成试卷失败: {e}", "error")
        finally:
            close_db(db_session)
    
    return render_template_string(generate_paper_template)

@app.route('/paper/<paper_id>')
def view_paper(paper_id):
    """查看试卷详情"""
    db_session = None
    paper = None
    paper_questions = []
    stats = {}
    
    try:
        db_session = get_db()
        paper = db_session.query(Paper).filter(Paper.id == paper_id).first()
        
        if not paper:
            flash("试卷不存在", "error")
            return redirect(url_for('papers'))
        
        # 获取试卷题目
        paper_questions = db_session.query(PaperQuestion).filter(
            PaperQuestion.paper_id == paper_id
        ).order_by(PaperQuestion.question_order).all()
        
        # 获取统计信息
        generator = PaperGenerator(db_session)
        stats = generator.get_paper_statistics(paper_id)
        
    except Exception as e:
        flash(f"获取试卷详情失败: {e}", "error")
    finally:
        close_db(db_session)
    
    return render_template_string(
        view_paper_template, 
        paper=paper, 
        paper_questions=paper_questions,
        stats=stats
    )

@app.route('/paper/<paper_id>/export')
def export_paper(paper_id):
    """导出试卷为 Word 文档"""
    db_session = None
    try:
        db_session = get_db()
        generator = PaperGenerator(db_session)
        
        docx_buffer = generator.export_paper_to_docx(paper_id)
        
        paper = db_session.query(Paper).filter(Paper.id == paper_id).first()
        
        # 确保即使paper_name为空，也能提供一个安全的文件名
        if paper is not None and paper.name is not None:
            paper_name = str(paper.name)
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            paper_name = f"无标题试卷_{timestamp}"

        safe_paper_name = secure_filename(paper_name)

        return send_file(
            docx_buffer,
            as_attachment=True,
            download_name=f'{safe_paper_name}.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        flash(f"导出试卷失败: {e}", "error")
        return redirect(url_for('view_paper', paper_id=paper_id))
    finally:
        close_db(db_session)

@app.route('/paper/<paper_id>/delete', methods=['POST'])
def delete_paper(paper_id):
    """删除试卷"""
    db_session = None
    
    try:
        db_session = get_db()
        paper = db_session.query(Paper).filter(Paper.id == paper_id).first()
        
        if not paper:
            flash("试卷不存在", "error")
            return redirect(url_for('papers'))
        
        db_session.delete(paper)
        db_session.commit()
        flash(f"试卷 '{paper.name}' 删除成功", "success")
        
    except Exception as e:
        flash(f"删除试卷失败: {e}", "error")
    finally:
        close_db(db_session)
    
    return redirect(url_for('papers'))

@app.route('/quick-generate', methods=['GET', 'POST'])
def quick_generate():
    """快速生成试卷"""
    if request.method == 'POST':
        try:
            db_session = get_db()
            generator = PaperGenerator(db_session)
            
            # 获取表单数据
            paper_name = request.form.get('paper_name', '').strip()
            difficulty_distribution = request.form.get('difficulty_distribution', 'balanced')
            
            if not paper_name:
                flash("试卷名称不能为空", "error")
                return redirect(url_for('quick_generate'))
            
            # 设置难度分布
            if difficulty_distribution == 'easy':
                distribution = {"1": 0.3, "2": 0.4, "3": 0.2, "4": 0.1, "5": 0.0}
            elif difficulty_distribution == 'hard':
                distribution = {"1": 0.0, "2": 0.1, "3": 0.2, "4": 0.4, "5": 0.3}
            else:  # balanced
                distribution = {"1": 0.1, "2": 0.2, "3": 0.4, "4": 0.2, "5": 0.1}
            
            # 生成试卷
            paper = generator.generate_paper_by_difficulty_distribution(
                paper_name=paper_name,
                paper_description=f"快速生成的{paper_name}",
                difficulty_distribution=distribution
            )
            
            flash(f"试卷 '{paper.name}' 生成成功！", "success")
            return redirect(url_for('view_paper', paper_id=paper.id))
            
        except Exception as e:
            flash(f"快速生成试卷失败: {e}", "error")
        finally:
            close_db(db_session)
    
    return render_template_string(quick_generate_template)

@app.route('/upload-paper-rule', methods=['GET', 'POST'])
def upload_paper_rule():
    """上传试卷规则Excel并自动组卷"""
    import pandas as pd
    from werkzeug.utils import secure_filename
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not file.filename:
            flash('请上传Excel文件或文件无名称', 'error')
            return redirect(url_for('upload_paper_rule'))
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        file.save(filepath)
        
        # 新增：获取多套组卷参数
        num_sets = int(request.form.get('num_sets', 1))
        if num_sets < 1:
            num_sets = 1
        if num_sets >10:
            num_sets = 10
        
        try:
            # 解析Sheet1（题型分布）
            df1 = pd.read_excel(filepath, sheet_name='题型分布')
            df1.columns = [str(col).strip().replace(' ', '').replace('　', '') for col in df1.columns]
            
            # 检查必需的列
            required_cols_s1 = {'题库名称', '题型', '题量', '每题分数'}
            if not required_cols_s1.issubset(df1.columns):
                missing_cols = required_cols_s1 - set(df1.columns)
                flash(f'题型分布表缺少必需列: {", ".join(missing_cols)}', 'error')
                return redirect(url_for('upload_paper_rule'))

            paper_structure = []
            for _, row in df1.iterrows():
                if pd.isna(row.get('题型')) or pd.isna(row.get('题量')) or pd.isna(row.get('每题分数')) or pd.isna(row.get('题库名称')):
                    continue
                qtype = str(row['题型']).split('（')[0]
                paper_structure.append({
                    'question_bank_name': str(row['题库名称']).strip(),
                    'question_type': qtype,
                    'count': int(row['题量']),
                    'score_per_question': float(row['每题分数'])
                })

            # 解析Sheet2（知识点分布）
            df2 = pd.read_excel(filepath, sheet_name='知识点分布', dtype=str)
            df2.columns = ['1级代码', '1级比重(%)', '2级代码', '2级比重(%)', '3级代码', '3级比重(%)']
            header_map = {
                '1级代码': ['1级代码', '一级代码', '1级 代码'],
                '1级比重(%)': ['1级比重(%)', '一级比重(%)', '1级比重%', '一级比重%'],
                '2级代码': ['2级代码', '二级代码', '2级 代码'],
                '2级比重(%)': ['2级比重(%)', '二级比重(%)', '2级比重%', '二级比重%'],
                '3级代码': ['3级代码', '三级代码', '3级 代码'],
                '3级比重(%)': ['3级比重(%)', '三级比重(%)', '3级比重%', '三级比重%'],
            }

            # 构建新表头映射
            new_columns = {}
            for std_col, aliases in header_map.items():
                for col in df2.columns:
                    if col in aliases:
                        new_columns[col] = std_col
            df2 = df2.rename(columns=new_columns)
            knowledge_distribution = {}
            if not df2.empty:
                required_cols_s2 = {'1级代码', '1级比重(%)', '2级代码', '2级比重(%)', '3级代码', '3级比重(%)'}
                if not required_cols_s2.issubset(df2.columns):
                    missing_cols = required_cols_s2 - set(df2.columns)
                    flash(f'知识点分布表缺少必需列: {", ".join(missing_cols)}', 'error')
                    return redirect(url_for('upload_paper_rule'))

                for _, row in df2.iterrows():
                    if row.isnull().all():
                        continue
                    l1 = str(row['1级代码']).strip()
                    l1r = float(row['1级比重(%)'])
                    l2 = str(row['2级代码']).strip()
                    l2r = float(row['2级比重(%)'])
                    l3 = str(row['3级代码']).strip()
                    l3r = float(row['3级比重(%)'])
                    if l1 not in knowledge_distribution:
                        knowledge_distribution[l1] = {'ratio': l1r, 'children': {}}
                    if l2 not in knowledge_distribution[l1]['children']:
                        knowledge_distribution[l1]['children'][l2] = {'ratio': l2r, 'children': {}}
                    knowledge_distribution[l1]['children'][l2]['children'][l3] = l3r
            
            # 从表单或Excel获取试卷名称
            paper_name = request.form.get('paper_name')
            if not paper_name:
                if paper_structure:
                    paper_name = f"{paper_structure[0]['question_bank_name']} - 自动组卷"
                else:
                    paper_name = f"自动组卷_{int(time.time())}"

            db_session = get_db()
            generator = PaperGenerator(db_session)
            paper_ids = []
            for i in range(num_sets):
                this_paper_name = paper_name if num_sets == 1 else f"{paper_name}_第{i+1}套"
                paper = generator.generate_paper_by_knowledge_distribution(
                    paper_name=this_paper_name,
                    paper_structure=paper_structure,
                    knowledge_distribution=knowledge_distribution
                )
                paper_ids.append(paper.id)
            flash(f'成功生成 {num_sets} 套试卷！', 'success')
            return redirect(url_for('papers'))
        except FileNotFoundError:
            flash("上传的文件未找到，请重试。", "error")
        except ValueError as e:
            flash(f"组卷失败，请检查规则配置：{e}", "error")
        except KeyError as e:
            flash(f"Excel文件中缺少必需的列名: {e}，请使用模板文件。", "error")
        except Exception as e:
            flash(f"处理文件时发生未知错误: {e}", "error")
        return redirect(url_for('upload_paper_rule')
    )

    # GET请求返回上传页面，增加多套组卷输入框
    return render_template_string('''
    <h2>上传试卷规则Excel</h2>
    <div style="margin-bottom: 20px;">
        <a href="/" class="btn">返回首页</a>
        <a href="/download-paper-rule-template" class="btn btn-success" style="margin-bottom:16px;display:inline-block;">下载组题规则模板</a>
    </div>
    <form method="post" enctype="multipart/form-data">
        <div class="form-group" style="margin-bottom: 1rem;">
            <label for="paper_name">试卷名称 (可选, 默认为题库名)</label>
            <input type="text" id="paper_name" name="paper_name" class="form-control" style="width:100%; padding:8px; border-radius:4px; border:1px solid #ccc;">
        </div>
        <div class="form-group">
            <label for="num_sets">生成套数</label>
            <input type="number" id="num_sets" name="num_sets" min="1" max="10" value="1" style="width:100px;">
        </div>
        <div class="form-group">
            <label for="file">上传组题规则文件</label>
            <input type="file" id="file" name="file" accept=".xlsx" required>
        </div>
        <button type="submit" style="padding:10px 20px; border-radius:5px; border:none; background-color:#007bff; color:white; cursor:pointer; margin-top:10px;">上传并自动组卷</button>
    </form>''')

# 组题功能模板
papers_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>试卷管理 - 题库管理系统</title>
    <style>body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .nav {
            background: #f8f9fa;
            padding: 15px 30px;
            border-bottom: 1px solid #e9ecef;
        }
        .nav a {
            color: #495057;
            text-decoration: none;
            margin-right: 20px;
            padding: 8px 16px;
            border-radius: 20px;
            transition: all 0.3s ease;
        }
        .nav a:hover {
            background: #007bff;
            color: white;
        }
        .nav a.active {
            background: #007bff;
            color: white;
        }
        .content {
            padding: 30px;
        }
        .actions {
            margin-bottom: 30px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            text-align: center;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-success {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
            color: white;
        }
        .btn-danger {
            background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
            color: white;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .papers-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        .paper-card {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        .paper-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        .paper-title {
            font-size: 1.3em;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }
        .paper-info {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 15px;
        }
        .paper-stats {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            font-size: 0.9em;
        }
        .paper-actions {
            display: flex;
            gap: 10px;
        }
        .btn-sm {
            padding: 6px 12px;
            font-size: 14px;
        }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
        }
        .empty-state h3 {
            margin-bottom: 10px;
            color: #495057;
        }
        .flash-messages {
            margin-bottom: 20px;
        }
        .flash-message {
            padding: 12px 20px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .flash-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .flash-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>试卷管理</h1>
            <p>管理和生成试卷</p>
        </div>
        
        <div class="nav" style="text-align: center; margin-bottom: 20px;">
            <a href="/" class="active">首页</a>
            <a href="/import-excel">导入题库</a>
            <a href="/papers">试卷管理</a>
            <a href="/quick-generate">快速生成</a>
            <a href="/generate-paper">自定义组题</a>
            <a href="/upload-paper-rule" class="btn btn-danger">上传组题规则</a>
            <a href="/banks" class="btn btn-info">题库管理</a>
        </div>
        
        <div class="content">
            <div class="flash-messages">{% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="flash-message flash-{{ category }}">{{ message }}</div>{% endfor %}
                    {% endif %}
                {% endwith %}
            </div>
            
            <div class="actions">
                <form id="batchForm" method="post" style="display:inline;">
                    <input type="hidden" name="paper_ids" id="batchPaperIds">
                    <button type="button" class="btn btn-success" onclick="batchExportExcel()">批量导出Excel</button>
                    <button type="button" class="btn btn-primary" onclick="batchExportWord()">批量导出Word</button>
                    <button type="button" class="btn btn-danger" onclick="batchDelete()">批量删除</button>
                </form>
                <a href="/quick-generate" class="btn btn-success">快速生成</a>
                <a href="/generate-paper" class="btn btn-primary">自定义组题</a>
            </div>
            <script>function getCheckedPaperIds() {
                let ids = [];
                document.querySelectorAll('.paper-checkbox:checked').forEach(cb =>ids.push(cb.value));
                return ids;
            }
            function batchExportExcel() {
                let ids = getCheckedPaperIds();
                if(ids.length===0){alert('请先选择试卷');return;}
                let form = document.getElementById('batchForm');
                form.action = '/export_papers_excel';
                document.getElementById('batchPaperIds').value = ids.join(',');
                form.submit();
            }
            function batchExportWord() {
                let ids = getCheckedPaperIds();
                if(ids.length===0){alert('请先选择试卷');return;}
                let form = document.getElementById('batchForm');
                form.action = '/export_papers_word';
                document.getElementById('batchPaperIds').value = ids.join(',');
                form.submit();
            }
            function batchDelete() {
                let ids = getCheckedPaperIds();
                if(ids.length===0){alert('请先选择试卷');return;}
                if(!confirm('确定要批量删除选中的试卷吗？'))return;
                let form = document.getElementById('batchForm');
                form.action = '/delete_papers';
                document.getElementById('batchPaperIds').value = ids.join(',');
                form.submit();
            }
            function toggleAllPapers(cb){
                document.querySelectorAll('.paper-checkbox').forEach(x=>x.checked=cb.checked);
            }
            </script>
            <div style="margin-bottom:10px;text-align:right;">
                <input type="checkbox" id="checkAll" onclick="toggleAllPapers(this)"> <label for="checkAll">全选</label>
            </div>{% if papers %}
            <div class="papers-grid">{% for paper in papers %}
                <div class="paper-card">
                    <input type="checkbox" class="paper-checkbox" value="{{ paper.id }}" style="float:right;transform:scale(1.3);margin-top:2px;">
                    <div class="paper-title">{{ paper.name }}</div>
                    <div class="paper-info">{{ paper.description or '暂无描述' }}
                    </div>
                    <div class="paper-stats">
                        <span>总分: {{ paper.total_score }}分</span>
                        <span>时长: {{ paper.duration }}分钟</span>
                    </div>
                    <div class="paper-stats">
                        <span>创建: {{ paper.created_at.strftime('%Y-%m-%d %H:%M') if paper.created_at else 'N/A' }}</span>
                        <span>难度: {{ paper.difficulty_level or '未设置' }}</span>
                    </div>
                    <div class="paper-actions">
                        <a href="/paper/{{ paper.id }}" class="btn btn-primary btn-sm">查看</a>
                        <a href="/paper/{{ paper.id }}/export" class="btn btn-success btn-sm">导出</a>
                        <a href="/paper/{{ paper.id }}/export_excel" class="btn btn-success btn-sm">Excel导出</a>
                        <form method="POST" action="/paper/{{ paper.id }}/delete" style="display: inline;" onsubmit="return confirm('确定要删除这个试卷吗？')">
                            <button type="submit" class="btn btn-danger btn-sm">删除</button>
                        </form>
                    </div>
                </div>{% endfor %}
            </div>{% else %}
            <div class="empty-state">
                <h3>暂无试卷</h3>
                <p>还没有生成任何试卷，点击上方按钮开始创建吧！</p>
            </div>{% endif %}
        </div>
    </div>
</body>
</html>"""

generate_paper_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>自定义组题 - 题库管理系统</title>
    <style>body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .nav {
            background: #f8f9fa;
            padding: 15px 30px;
            border-bottom: 1px solid #e9ecef;
        }
        .nav a {
            color: #495057;
            text-decoration: none;
            margin-right: 20px;
            padding: 8px 16px;
            border-radius: 20px;
            transition: all 0.3s ease;
        }
        .nav a:hover {
            background: #007bff;
            color: white;
        }
        .nav a.active {
            background: #007bff;
            color: white;
        }
        .content {
            padding: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #333;
        }
        .form-control {
            width: 100%;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }
        .form-control:focus {
            outline: none;
            border-color: #667eea;
        }
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            text-align: center;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-success {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
            color: white;
        }
        .btn-danger {
            background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
            color: white;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .rules-container {
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .rule-item {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .rule-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .rule-title {
            font-weight: 600;
            color: #333;
        }
        .remove-rule {
            background: #ff416c;
            color: white;
            border: none;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            cursor: pointer;
            font-size: 16px;
        }
        .rule-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .flash-messages {
            margin-bottom: 20px;
        }
        .flash-message {
            padding: 12px 20px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .flash-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .flash-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>自定义组题</h1>
            <p>根据规则自动生成试卷</p>
        </div>
        
        <div class="nav">
            <a href="/" class="active">首页</a>
            <a href="/import-excel">导入题库</a>
            <a href="/papers">试卷管理</a>
            <a href="/quick-generate">快速生成</a>
            <a href="/generate-paper" class="active">自定义组题</a>
            <a href="/upload-paper-rule" class="btn btn-danger">上传组题规则</a>
            <a href="/banks" class="btn btn-info">题库管理</a>
        </div>
        
        <div class="content">
            <div class="flash-messages">{% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="flash-message flash-{{ category }}">{{ message }}</div>{% endfor %}
                    {% endif %}
                {% endwith %}
            </div>
            
            <form method="POST" id="generateForm">
                <div class="form-row">
                    <div class="form-group">
                        <label for="paper_name">试卷名称 *</label>
                        <input type="text" id="paper_name" name="paper_name" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="difficulty_level">试卷难度</label>
                        <select id="difficulty_level" name="difficulty_level" class="form-control">
                            <option value="简单">简单</option>
                            <option value="中等" selected>中等</option>
                            <option value="困难">困难</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="total_score">试卷总分</label>
                        <input type="number" id="total_score" name="total_score" class="form-control" value="100" min="1" max="200">
                    </div>
                    <div class="form-group">
                        <label for="duration">考试时长（分钟）</label>
                        <input type="number" id="duration" name="duration" class="form-control" value="120" min="30" max="300">
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="paper_description">试卷描述</label>
                    <textarea id="paper_description" name="paper_description" class="form-control" rows="3" placeholder="可选：试卷的详细描述"></textarea>
                </div>
                
                <div class="rules-container">
                    <h3>组题规则</h3>
                    <div id="rulesList">
                        <!-- 规则项将在这里动态添加 -->
                    </div>
                    <button type="button" class="btn btn-success" onclick="addRule()">➕ 添加规则</button>
                </div>
                
                <div class="form-group">
                    <button type="submit" class="btn btn-primary">生成试卷</button>
                    <a href="/papers" class="btn btn-danger">取消</a>
                </div>
                
                <input type="hidden" id="rule_count" name="rule_count" value="0">
            </form>
        </div>
    </div>
    
    <script>let ruleIndex = 0;
        
        function addRule() {
            const rulesList = document.getElementById('rulesList');
            const ruleDiv = document.createElement('div');
            ruleDiv.className = 'rule-item';
            ruleDiv.innerHTML = `
                <div class="rule-header">
                    <span class="rule-title">规则 ${ruleIndex + 1}</span>
                    <button type="button" class="remove-rule" onclick="removeRule(this)">×</button>
                </div>
                <div class="rule-grid">
                    <div class="form-group">
                        <label>题型</label>
                        <select name="rule_${ruleIndex}_type" class="form-control" required>
                            <option value="">请选择题型</option>
                            <option value="B">B（单选题）</option>
                            <option value="G">G（多选题）</option>
                            <option value="C">C（判断题）</option>
                            <option value="T">T（填空题）</option>
                            <option value="D">D（简答题）</option>
                            <option value="U">U（计算题）</option>
                            <option value="W">W（论述题）</option>
                            <option value="E">E（案例分析题）</option>
                            <option value="F">F（综合题）</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>难度</label>
                        <select name="rule_${ruleIndex}_difficulty" class="form-control" required>
                            <option value="">请选择难度</option>
                            <option value="1">1（很简单）</option>
                            <option value="2">2（简单）</option>
                            <option value="3">3（中等）</option>
                            <option value="4">4（困难）</option>
                            <option value="5">5（很难）</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>题目数量</label>
                        <input type="number" name="rule_${ruleIndex}_count" class="form-control" value="1" min="1" max="50" required>
                    </div>
                    <div class="form-group">
                        <label>每题分值</label>
                        <input type="number" name="rule_${ruleIndex}_score" class="form-control" value="5.0" min="0.5" max="50" step="0.5" required>
                    </div>
                    <div class="form-group">
                        <label>章节名称</label>
                        <input type="text" name="rule_${ruleIndex}_section" class="form-control" placeholder="如：单选题、多选题等">
                    </div>
                </div>`;
            rulesList.appendChild(ruleDiv);
            ruleIndex++;
            document.getElementById('rule_count').value = ruleIndex;
        }
        
        function removeRule(button) {
            button.parentElement.parentElement.remove();
            updateRuleNumbers();
        }
        
        function updateRuleNumbers() {
            const rules = document.querySelectorAll('.rule-item');
            rules.forEach((rule, index) =>{
                rule.querySelector('.rule-title').textContent = `规则 ${index + 1}`;
            });
            ruleIndex = rules.length;
            document.getElementById('rule_count').value = ruleIndex;
        }
        
        // 页面加载时添加一个默认规则
        window.onload = function() {
            addRule();
        };
    </script>
</body>
</html>"""

view_paper_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ paper.name }} - 题库管理系统</title>
    <style>body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .nav {
            background: #f8f9fa;
            padding: 15px 30px;
            border-bottom: 1px solid #e9ecef;
        }
        .nav a {
            color: #495057;
            text-decoration: none;
            margin-right: 20px;
            padding: 8px 16px;
            border-radius: 20px;
            transition: all 0.3s ease;
        }
        .nav a:hover {
            background: #007bff;
            color: white;
        }
        .nav a.active {
            background: #007bff;
            color: white;
        }
        .content {
            padding: 30px;
        }
        .paper-info {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .paper-title {
            font-size: 2em;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }
        .paper-meta {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }
        .meta-item {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #666;
        }
        .paper-description {
            color: #666;
            font-style: italic;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 5px;
        }
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        .questions-section {
            margin-bottom: 30px;
        }
        .section-title {
            font-size: 1.5em;
            font-weight: 600;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }
        .question-item {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
        }
        .question-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .question-number {
            font-weight: 600;
            color: #667eea;
            font-size: 1.1em;
        }
        .question-score {
            background: #28a745;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.9em;
        }
        .question-stem {
            color: #333;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        .question-options {
            margin-left: 20px;
        }
        .option {
            margin-bottom: 8px;
            color: #666;
        }
        .actions {
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            text-align: center;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-success {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
            color: white;
        }
        .btn-danger {
            background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
            color: white;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .flash-messages {
            margin-bottom: 20px;
        }
        .flash-message {
            padding: 12px 20px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .flash-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .flash-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ paper.name }}</h1>
            <p>试卷详情</p>
        </div>
        
        <div class="nav">
            <a href="/" class="active">首页</a>
            <a href="/import-excel">导入题库</a>
            <a href="/papers">试卷管理</a>
            <a href="/quick-generate">快速生成</a>
            <a href="/generate-paper">自定义组题</a>
            <a href="/upload-paper-rule" class="btn btn-danger">上传组题规则</a>
            <a href="/banks" class="btn btn-info">题库管理</a>
        </div>
        
        <div class="content">
            <div class="flash-messages">{% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="flash-message flash-{{ category }}">{{ message }}</div>{% endfor %}
                    {% endif %}
                {% endwith %}
            </div>
            
            <div class="paper-info">
                <div class="paper-title">{{ paper.name }}</div>
                <div class="paper-meta">
                    <div class="meta-item">
                        <span>总分:</span>
                        <span>{{ paper.total_score }}分</span>
                    </div>
                    <div class="meta-item">
                        <span>时长:</span>
                        <span>{{ paper.duration }}分钟</span>
                    </div>
                    <div class="meta-item">
                        <span>难度:</span>
                        <span>{{ paper.difficulty_level or '未设置' }}</span>
                    </div>
                    <div class="meta-item">
                        <span>创建:</span>
                        <span>{{ paper.created_at.strftime('%Y-%m-%d %H:%M') if paper.created_at else 'N/A' }}</span>
                    </div>
                </div>{% if paper.description %}
                <div class="paper-description">{{ paper.description }}</div>{% endif %}
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{{ stats.total_questions or 0 }}</div>
                    <div class="stat-label">总题目数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ stats.total_score or 0 }}</div>
                    <div class="stat-label">实际总分</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ stats.question_types|length or 0 }}</div>
                    <div class="stat-label">题型种类</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ stats.sections|length or 0 }}</div>
                    <div class="stat-label">章节数量</div>
                </div>
            </div>
            
            <div class="questions-section">
                <div class="section-title">题目列表</div>{% if paper_questions %}
                    {% for pq in paper_questions %}
                    <div class="question-item">
                        <div class="question-header">
                            <span class="question-number">第{{ pq.question_order }}题</span>
                            <span class="question-score">{{ pq.score }}分</span>
                        </div>
                        <div class="question-stem">{{ pq.question.stem }}</div>{% if pq.question.option_a or pq.question.option_b or pq.question.option_c or pq.question.option_d or pq.question.option_e %}
                        <div class="question-options">{% if pq.question.option_a %}<div class="option">A. {{ pq.question.option_a }}</div>{% endif %}
                            {% if pq.question.option_b %}<div class="option">B. {{ pq.question.option_b }}</div>{% endif %}
                            {% if pq.question.option_c %}<div class="option">C. {{ pq.question.option_c }}</div>{% endif %}
                            {% if pq.question.option_d %}<div class="option">D. {{ pq.question.option_d }}</div>{% endif %}
                            {% if pq.question.option_e %}<div class="option">E. {{ pq.question.option_e }}</div>{% endif %}
                        </div>{% endif %}
                        <div style="margin-top: 10px; color: #666; font-size: 0.9em;">
                            <span>题型: {{ pq.question.question_type_code }}</span>| 
                            <span>难度: {{ pq.question.difficulty_code }}</span>{% if pq.section_name %} | <span>章节: {{ pq.section_name }}</span>{% endif %}
                        </div>
                    </div>{% endfor %}
                {% else %}
                    <div style="text-align: center; padding: 40px; color: #6c757d;">
                        <h3>暂无题目</h3>
                        <p>这个试卷还没有添加任何题目。</p>
                    </div>{% endif %}
            </div>
            
            <div class="actions">
                <a href="/paper/{{ paper.id }}/export" class="btn btn-success">导出试卷</a>
                <a href="/papers" class="btn btn-primary">返回列表</a>
                <form method="POST" action="/paper/{{ paper.id }}/delete" style="display: inline;" onsubmit="return confirm('确定要删除这个试卷吗？')">
                    <button type="submit" class="btn btn-danger">删除试卷</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>"""

quick_generate_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>快速生成试卷 - 题库管理系统</title>
    <style>body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .nav {
            background: #f8f9fa;
            padding: 15px 30px;
            border-bottom: 1px solid #e9ecef;
        }
        .nav a {
            color: #495057;
            text-decoration: none;
            margin-right: 20px;
            padding: 8px 16px;
            border-radius: 20px;
            transition: all 0.3s ease;
        }
        .nav a:hover {
            background: #007bff;
            color: white;
        }
        .nav a.active {
            background: #007bff;
            color: white;
        }
        .content {
            padding: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #333;
        }
        .form-control {
            width: 100%;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }
        .form-control:focus {
            outline: none;
            border-color: #667eea;
        }
        .difficulty-options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 10px;
        }
        .difficulty-option {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
        }
        .difficulty-option:hover {
            border-color: #667eea;
            background: #e3f2fd;
        }
        .difficulty-option.selected {
            border-color: #667eea;
            background: #667eea;
            color: white;
        }
        .difficulty-option input[type="radio"] {
            display: none;
        }
        .difficulty-title {
            font-weight: 600;
            margin-bottom: 5px;
        }
        .difficulty-desc {
            font-size: 0.9em;
            opacity: 0.8;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            text-align: center;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-danger {
            background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
            color: white;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .flash-messages {
            margin-bottom: 20px;
        }
        .flash-message {
            padding: 12px 20px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .flash-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .flash-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>快速生成试卷</h1>
            <p>一键生成标准试卷</p>
        </div>
        
        <div class="nav">
            <a href="/">首页</a>
            <a href="/import-excel">导入题库</a>
            <a href="/papers">试卷管理</a>
            <a href="/quick-generate" class="active">快速生成</a>
            <a href="/generate-paper">自定义组题</a>
            <a href="/upload-paper-rule" class="btn btn-danger">上传组题规则</a>
            <a href="/banks" class="btn btn-info">题库管理</a>
        </div>
        
        <div class="content">
            <div class="flash-messages">{% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="flash-message flash-{{ category }}">{{ message }}</div>{% endfor %}
                    {% endif %}
                {% endwith %}
            </div>
            
            <form method="POST">
                <div class="form-group">
                    <label for="paper_name">试卷名称 *</label>
                    <input type="text" id="paper_name" name="paper_name" class="form-control" required placeholder="如：2024年春季考试试卷">
                </div>
                
                <div class="form-group">
                    <label>难度分布</label>
                    <div class="difficulty-options">
                        <label class="difficulty-option" onclick="selectDifficulty('easy')">
                            <input type="radio" name="difficulty_distribution" value="easy">
                            <div class="difficulty-title">简单</div>
                            <div class="difficulty-desc">适合基础测试</div>
                        </label>
                        <label class="difficulty-option selected" onclick="selectDifficulty('balanced')">
                            <input type="radio" name="difficulty_distribution" value="balanced" checked>
                            <div class="difficulty-title">平衡</div>
                            <div class="difficulty-desc">标准难度分布</div>
                        </label>
                        <label class="difficulty-option" onclick="selectDifficulty('hard')">
                            <input type="radio" name="difficulty_distribution" value="hard">
                            <div class="difficulty-title">困难</div>
                            <div class="difficulty-desc">适合挑战性测试</div>
                        </label>
                    </div>
                </div>
                
                <div class="form-group">
                    <button type="submit" class="btn btn-primary">生成试卷</button>
                    <a href="/papers" class="btn btn-danger">取消</a>
                </div>
            </form>
        </div>
    </div>
    
    <script>function selectDifficulty(value) {
            // 移除所有选中状态
            document.querySelectorAll('.difficulty-option').forEach(option =>{
                option.classList.remove('selected');
            });
            
            // 选中当前选项
            event.currentTarget.classList.add('selected');
            
            // 设置radio值
            document.querySelector(`input[value="${value}"]`).checked = true;
        }
    </script>
</body>
</html>"""

@app.route('/banks', methods=['GET', 'POST'])
def manage_banks():
    """管理和查看题库"""
    db_session = get_db()
    try:
        if request.method == 'POST':
            bank_name = request.form.get('bank_name', '').strip()
            if bank_name:
                existing_bank = db_session.query(QuestionBank).filter_by(name=bank_name).first()
                if not existing_bank:
                    new_bank = QuestionBank(name=bank_name)
                    db_session.add(new_bank)
                    db_session.commit()
                    flash(f'题库 "{bank_name}" 创建成功！', 'success')
                else:
                    flash(f'题库 "{bank_name}" 已存在。', 'warning')
            else:
                flash('题库名称不能为空。', 'error')
            return redirect(url_for('manage_banks'))
        
        banks = db_session.query(QuestionBank).order_by(QuestionBank.created_at.desc()).all()
    except Exception as e:
        flash(f"操作失败：{e}", "error")
        banks = []
    finally:
        close_db(db_session)
        
    return render_template_string(banks_template, banks=banks)

@app.route('/download-paper-rule-template', methods=['GET'])
def download_paper_rule_template():
    """生成并下载组题规则Excel模板"""
    import pandas as pd
    output = BytesIO()
    # Sheet1: 题型分布
    df1 = pd.DataFrame([
        ['保卫管理员（三级）理论', 'B（单选题）', 10, 2]
    ])
    df1.columns = ['题库名称', '题型', '题量', '每题分数']
    # Sheet2: 知识点分布
    df2 = pd.DataFrame([
        ['A', 50, 'B', 60, 'C', 100]
    ])
    df2.columns = ['1级代码', '1级比重(%)', '2级代码', '2级比重(%)', '3级代码', '3级比重(%)']
    with pd.ExcelWriter(output, engine='openpyxl') as writer: # type: ignore
        df1.to_excel(writer, index=False, sheet_name='题型分布')
        df2.to_excel(writer, index=False, sheet_name='知识点分布')
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='组题规则模板.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/paper/<paper_id>/export_excel')
def export_paper_excel(paper_id):
    """导出单套试卷为Excel，结构与题库导入模板一致"""
    import pandas as pd
    db_session = None
    try:
        db_session = get_db()
        paper = db_session.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            flash("试卷不存在", "error")
            return redirect(url_for('papers'))
        paper_questions = db_session.query(PaperQuestion).filter(PaperQuestion.paper_id == paper_id).order_by(PaperQuestion.question_order).all()
        # 构造DataFrame
        data = []
        for pq in paper_questions:
            q = pq.question
            data.append({
                '题库名称': q.question_bank.name if q.question_bank else '',
                'ID': q.id,
                '序号': pq.question_order,
                '认定点代码': '',
                '题型代码': q.question_type_code,
                '题号': '',
                '试题（题干）': q.stem,
                '试题（选项A）': q.option_a,
                '试题（选项B）': q.option_b,
                '试题（选项C）': q.option_c,
                '试题（选项D）': q.option_d,
                '试题（选项E）': q.option_e,
                '【图】及位置': q.image_info,
                '正确答案': q.correct_answer,
                '难度代码': q.difficulty_code,
                '一致性代码': q.consistency_code,
                '解析': q.analysis
            })
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:  # type: ignore
            df.to_excel(writer, index=False, sheet_name='题库模板')
        output.seek(0)
        paper_name_str = str(paper.name) if paper.name is not None else ''
        safe_paper_name = secure_filename(paper_name_str if paper_name_str else f"试卷_{paper_id}")
        return send_file(
            output,
            as_attachment=True,
            download_name=f'{safe_paper_name}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        flash(f"导出Excel失败: {e}", "error")
        return redirect(url_for('view_paper', paper_id=paper_id))
    finally:
        close_db(db_session)

@app.route('/export_papers_excel', methods=['POST'])
def export_papers_excel():
    """批量导出多套试卷到一个Excel文件（多Sheet）"""
    import pandas as pd
    db_session = None
    try:
        db_session = get_db()
        paper_ids = request.form.get('paper_ids', '')
        if not paper_ids:
            flash('未选择试卷', 'error')
            return redirect(url_for('papers'))
        paper_ids = [pid.strip() for pid in paper_ids.split(',') if pid.strip()]
        if not paper_ids:
            flash('未选择试卷', 'error')
            return redirect(url_for('papers'))
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for idx, pid in enumerate(paper_ids):
                paper = db_session.query(Paper).filter(Paper.id == pid).first()
                if not paper:
                    continue
                paper_questions = db_session.query(PaperQuestion).filter(PaperQuestion.paper_id == pid).order_by(PaperQuestion.question_order).all()
                data = []
                for pq in paper_questions:
                    q = pq.question
                    data.append({
                        '题库名称': q.question_bank.name if q.question_bank else '',
                        'ID': q.id,
                        '序号': pq.question_order,
                        '认定点代码': '',
                        '题型代码': q.question_type_code,
                        '题号': '',
                        '试题（题干）': q.stem,
                        '试题（选项A）': q.option_a,
                        '试题（选项B）': q.option_b,
                        '试题（选项C）': q.option_c,
                        '试题（选项D）': q.option_d,
                        '试题（选项E）': q.option_e,
                        '【图】及位置': q.image_info,
                        '正确答案': q.correct_answer,
                        '难度代码': q.difficulty_code,
                        '一致性代码': q.consistency_code,
                        '解析': q.analysis
                    })
                df = pd.DataFrame(data)
                sheet_name = paper.name if paper.name else f"试卷{idx+1}"
                # Excel sheet名不能超过31字符
                sheet_name = sheet_name[:31]
                df.to_excel(writer, index=False, sheet_name=sheet_name)
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name='批量导出试卷.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        flash(f'批量导出Excel失败: {e}', 'error')
        return redirect(url_for('papers'))
    finally:
        close_db(db_session)

@app.route('/bank/<bank_id>/delete', methods=['POST'])
def delete_bank(bank_id):
    """删除题库及其下所有题目"""
    db_session = get_db()
    try:
        bank = db_session.query(QuestionBank).filter_by(id=bank_id).first()
        if not bank:
            flash('题库不存在。', 'error')
        else:
            db_session.delete(bank)
            db_session.commit()
            flash(f'题库 "{bank.name}" 及其下所有题目已删除。', 'success')
    except Exception as e:
        db_session.rollback()
        flash(f'删除题库失败：{e}', 'error')
    finally:
        close_db(db_session)
    return redirect(url_for('manage_banks'))

@app.route('/export_papers_word', methods=['POST'])
def export_papers_word():
    """批量导出多套试卷到一个Word文件（合并）"""
    from docx import Document
    db_session = None
    try:
        db_session = get_db()
        paper_ids = request.form.get('paper_ids', '')
        if not paper_ids:
            flash('未选择试卷', 'error')
            return redirect(url_for('papers'))
        paper_ids = [pid.strip() for pid in paper_ids.split(',') if pid.strip()]
        if not paper_ids:
            flash('未选择试卷', 'error')
            return redirect(url_for('papers'))
        doc = Document()
        for idx, pid in enumerate(paper_ids):
            generator = PaperGenerator(db_session)
            try:
                sub_doc = generator.export_paper_to_docx(pid)
                sub_doc.seek(0)
                sub = Document(sub_doc)
                if idx >0:
                    doc.add_page_break()
                for element in sub.element.body:
                    doc.element.body.append(element)
            except Exception as e:
                flash(f'导出试卷 {pid} 失败: {e}', 'error')
        output = BytesIO()
        doc.save(output)
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name='批量导出试卷.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        flash(f'批量导出Word失败: {e}', 'error')
        return redirect(url_for('papers'))
    finally:
        close_db(db_session)

@app.route('/delete_papers', methods=['POST'])
def delete_papers():
    """批量删除试卷"""
    db_session = None
    try:
        db_session = get_db()
        paper_ids = request.form.get('paper_ids', '')
        if not paper_ids:
            flash('未选择试卷', 'error')
            return redirect(url_for('papers'))
        paper_ids = [pid.strip() for pid in paper_ids.split(',') if pid.strip()]
        if not paper_ids:
            flash('未选择试卷', 'error')
            return redirect(url_for('papers'))
        deleted = 0
        for pid in paper_ids:
            paper = db_session.query(Paper).filter(Paper.id == pid).first()
            if paper:
                db_session.delete(paper)
                deleted += 1
        db_session.commit()
        flash(f'成功删除 {deleted} 套试卷', 'success')
    except Exception as e:
        flash(f'批量删除失败: {e}', 'error')
    finally:
        close_db(db_session)
    return redirect(url_for('papers'))

@app.route('/export-excel', methods=['GET'])
def handle_export_excel():
    """导出题库为Excel文件"""
    db = get_db()
    try:
        # 生成唯一的文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'questions_export_{timestamp}.xlsx')
        
        # 导出题库
        count = export_db_questions_to_excel(db, output_path)
        
        if count >0:
            # 返回文件下载
            return send_file(
                output_path,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'题库导出_{timestamp}.xlsx'
            )
        else:
            flash("题库中没有题目可导出。", "warning")
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f"导出题库失败: {e}", "error")
        return redirect(url_for('index'))
    finally:
        close_db(db)

if __name__ == '__main__':
    print("Starting Flask application...")
    app.run(debug=True, host='0.0.0.0', port=5000)
