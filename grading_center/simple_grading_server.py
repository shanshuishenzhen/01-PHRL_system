#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版阅卷中心服务器
使用Python Flask替代Node.js，避免复杂的依赖问题
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from flask import Flask, render_template_string, jsonify, request, send_from_directory
    from flask_cors import CORS
except ImportError:
    print("错误: 缺少Flask依赖，请运行: pip install flask flask-cors")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# 配置
app.config['SECRET_KEY'] = 'grading-center-secret-key'
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'grading_center.db')

def init_database():
    """初始化数据库"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'teacher',
            real_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建考试结果表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exam_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            exam_id TEXT NOT NULL,
            answers TEXT,
            score REAL,
            graded_by TEXT,
            graded_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建阅卷任务表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grading_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_result_id INTEGER,
            teacher_id TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (exam_result_id) REFERENCES exam_results (id)
        )
    ''')
    
    # 插入默认管理员用户
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, role, real_name)
        VALUES ('admin', 'admin123', 'admin', '系统管理员')
    ''')
    
    conn.commit()
    conn.close()

# HTML模板
MAIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PH&RL 阅卷中心</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Microsoft YaHei', sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 1rem; text-align: center; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        .card { background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .card-header { background: #3498db; color: white; padding: 1rem; border-radius: 8px 8px 0 0; }
        .card-body { padding: 1.5rem; }
        .btn { padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; margin: 0.25rem; }
        .btn-primary { background: #3498db; color: white; }
        .btn-success { background: #27ae60; color: white; }
        .btn-warning { background: #f39c12; color: white; }
        .btn:hover { opacity: 0.8; }
        .status { padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; }
        .status-pending { background: #f39c12; color: white; }
        .status-graded { background: #27ae60; color: white; }
        .status-reviewing { background: #3498db; color: white; }
        table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
        th, td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: bold; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .stat-card { background: white; padding: 1.5rem; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .stat-number { font-size: 2rem; font-weight: bold; color: #3498db; }
        .stat-label { color: #666; margin-top: 0.5rem; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏛️ PH&RL 在线考试系统 - 阅卷中心</h1>
        <p>专业的在线阅卷平台</p>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="totalExams">0</div>
                <div class="stat-label">待阅卷考试</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="gradedExams">0</div>
                <div class="stat-label">已阅卷考试</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="avgScore">0</div>
                <div class="stat-label">平均分数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalTeachers">1</div>
                <div class="stat-label">阅卷教师</div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h2>📝 阅卷任务列表</h2>
            </div>
            <div class="card-body">
                <button class="btn btn-primary" onclick="refreshTasks()">🔄 刷新任务</button>
                <button class="btn btn-success" onclick="autoGrade()">🤖 自动阅卷</button>
                <button class="btn btn-warning" onclick="exportResults()">📊 导出结果</button>
                
                <table id="tasksTable">
                    <thead>
                        <tr>
                            <th>考试ID</th>
                            <th>学生ID</th>
                            <th>提交时间</th>
                            <th>状态</th>
                            <th>分数</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody id="tasksBody">
                        <tr>
                            <td colspan="6" style="text-align: center; color: #666;">
                                暂无阅卷任务，请等待学生提交考试...
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h2>ℹ️ 系统信息</h2>
            </div>
            <div class="card-body">
                <p><strong>服务状态:</strong> <span style="color: #27ae60;">✅ 正常运行</span></p>
                <p><strong>数据库:</strong> SQLite ({{ database_path }})</p>
                <p><strong>启动时间:</strong> {{ start_time }}</p>
                <p><strong>版本:</strong> v1.0.0</p>
                <p><strong>端口:</strong> 5173</p>
            </div>
        </div>
    </div>
    
    <script>
        function refreshTasks() {
            fetch('/api/tasks')
                .then(response => response.json())
                .then(data => {
                    updateTasksTable(data.tasks);
                    updateStats(data.stats);
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('刷新失败: ' + error.message);
                });
        }
        
        function updateTasksTable(tasks) {
            const tbody = document.getElementById('tasksBody');
            if (tasks.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #666;">暂无阅卷任务</td></tr>';
                return;
            }
            
            tbody.innerHTML = tasks.map(task => `
                <tr>
                    <td>${task.exam_id}</td>
                    <td>${task.student_id}</td>
                    <td>${task.created_at}</td>
                    <td><span class="status status-${task.status}">${getStatusText(task.status)}</span></td>
                    <td>${task.score || '-'}</td>
                    <td>
                        <button class="btn btn-primary" onclick="gradeTask(${task.id})">阅卷</button>
                    </td>
                </tr>
            `).join('');
        }
        
        function updateStats(stats) {
            document.getElementById('totalExams').textContent = stats.total || 0;
            document.getElementById('gradedExams').textContent = stats.graded || 0;
            document.getElementById('avgScore').textContent = (stats.avg_score || 0).toFixed(1);
        }
        
        function getStatusText(status) {
            const statusMap = {
                'pending': '待阅卷',
                'graded': '已阅卷',
                'reviewing': '复核中'
            };
            return statusMap[status] || status;
        }
        
        function autoGrade() {
            fetch('/api/auto-grade', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(`自动阅卷完成！处理了 ${data.processed} 个任务`);
                    refreshTasks();
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('自动阅卷失败: ' + error.message);
                });
        }
        
        function gradeTask(taskId) {
            const score = prompt('请输入分数 (0-100):');
            if (score === null) return;
            
            fetch(`/api/tasks/${taskId}/grade`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ score: parseFloat(score) })
            })
            .then(response => response.json())
            .then(data => {
                alert('阅卷完成！');
                refreshTasks();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('阅卷失败: ' + error.message);
            });
        }
        
        function exportResults() {
            window.open('/api/export', '_blank');
        }
        
        // 页面加载时刷新数据
        document.addEventListener('DOMContentLoaded', refreshTasks);
        
        // 每30秒自动刷新
        setInterval(refreshTasks, 30000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """主页"""
    return render_template_string(MAIN_TEMPLATE, 
                                database_path=DATABASE_PATH,
                                start_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/api/tasks')
def get_tasks():
    """获取阅卷任务列表"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 获取任务列表
    cursor.execute('''
        SELECT er.id, er.student_id, er.exam_id, er.score, er.created_at,
               CASE WHEN er.score IS NULL THEN 'pending' ELSE 'graded' END as status
        FROM exam_results er
        ORDER BY er.created_at DESC
        LIMIT 50
    ''')
    
    tasks = []
    for row in cursor.fetchall():
        tasks.append({
            'id': row[0],
            'student_id': row[1],
            'exam_id': row[2],
            'score': row[3],
            'created_at': row[4],
            'status': row[5]
        })
    
    # 获取统计信息
    cursor.execute('SELECT COUNT(*) FROM exam_results WHERE score IS NULL')
    total_pending = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM exam_results WHERE score IS NOT NULL')
    total_graded = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(score) FROM exam_results WHERE score IS NOT NULL')
    avg_score = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return jsonify({
        'tasks': tasks,
        'stats': {
            'total': total_pending,
            'graded': total_graded,
            'avg_score': avg_score
        }
    })

@app.route('/api/tasks/<int:task_id>/grade', methods=['POST'])
def grade_task(task_id):
    """阅卷"""
    data = request.get_json()
    score = data.get('score', 0)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE exam_results 
        SET score = ?, graded_by = 'admin', graded_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (score, task_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': '阅卷完成'})

@app.route('/api/auto-grade', methods=['POST'])
def auto_grade():
    """自动阅卷"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 获取未阅卷的任务
    cursor.execute('SELECT id FROM exam_results WHERE score IS NULL')
    tasks = cursor.fetchall()
    
    # 简单的自动阅卷逻辑（随机分数）
    import random
    processed = 0
    for task in tasks:
        score = random.randint(60, 95)  # 随机分数
        cursor.execute('''
            UPDATE exam_results 
            SET score = ?, graded_by = 'auto', graded_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (score, task[0]))
        processed += 1
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'processed': processed})

@app.route('/api/export')
def export_results():
    """导出结果"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT student_id, exam_id, score, graded_by, graded_at, created_at
        FROM exam_results
        WHERE score IS NOT NULL
        ORDER BY created_at DESC
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    # 生成CSV格式
    import io
    output = io.StringIO()
    output.write('学生ID,考试ID,分数,阅卷人,阅卷时间,提交时间\n')
    
    for row in results:
        output.write(f'{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]}\n')
    
    from flask import Response
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=grading_results.csv'}
    )

if __name__ == '__main__':
    print("🚀 启动PH&RL阅卷中心...")
    print("=" * 50)
    
    # 初始化数据库
    init_database()
    print("✅ 数据库初始化完成")
    
    # 启动服务器
    print("🌐 启动Web服务器...")
    print("📍 访问地址: http://localhost:5173")
    print("👤 默认账户: admin / admin123")
    print("=" * 50)
    
    try:
        app.run(host='0.0.0.0', port=5173, debug=False)
    except KeyboardInterrupt:
        print("\n👋 阅卷中心已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
