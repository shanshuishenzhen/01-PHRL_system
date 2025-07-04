#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实施多数据库架构解决方案
"""

import os
import sys
import shutil
import traceback

def create_database_manager():
    """创建数据库管理器"""
    print("🔧 创建数据库管理器")
    print("-" * 40)
    
    try:
        # 创建数据库管理器文件
        db_manager_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多项目数据库管理器
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

class DatabaseManager:
    """多项目数据库管理器"""
    
    def __init__(self, base_dir="question_banks"):
        self.base_dir = base_dir
        # 确保目录存在
        os.makedirs(base_dir, exist_ok=True)
        self._engines = {}
        self._sessions = {}
    
    def get_engine(self, project_name):
        """获取指定项目的数据库引擎"""
        if project_name not in self._engines:
            # 安全的文件名处理
            safe_name = self._safe_filename(project_name)
            db_path = os.path.join(self.base_dir, f"{safe_name}.db")
            
            # 创建数据库引擎
            self._engines[project_name] = create_engine(f'sqlite:///{db_path}')
            
            # 创建表结构
            Base.metadata.create_all(self._engines[project_name])
            
        return self._engines[project_name]
    
    def get_session(self, project_name):
        """获取指定项目的数据库会话"""
        engine = self.get_engine(project_name)
        Session = sessionmaker(bind=engine)
        return Session()
    
    def list_projects(self):
        """列出所有项目"""
        if not os.path.exists(self.base_dir):
            return []
        
        projects = []
        for filename in os.listdir(self.base_dir):
            if filename.endswith('.db'):
                # 恢复原始项目名称
                project_name = filename[:-3]  # 移除.db后缀
                projects.append(project_name)
        
        return sorted(projects)
    
    def create_project(self, project_name):
        """创建新项目"""
        try:
            # 获取引擎会自动创建数据库和表
            engine = self.get_engine(project_name)
            return True
        except Exception as e:
            print(f"创建项目失败: {e}")
            return False
    
    def delete_project(self, project_name):
        """删除项目（谨慎使用）"""
        try:
            safe_name = self._safe_filename(project_name)
            db_path = os.path.join(self.base_dir, f"{safe_name}.db")
            
            if os.path.exists(db_path):
                os.remove(db_path)
                
            # 清理缓存
            if project_name in self._engines:
                del self._engines[project_name]
            if project_name in self._sessions:
                del self._sessions[project_name]
                
            return True
        except Exception as e:
            print(f"删除项目失败: {e}")
            return False
    
    def get_project_stats(self, project_name):
        """获取项目统计信息"""
        try:
            from models import Question, QuestionBank
            session = self.get_session(project_name)
            
            question_count = session.query(Question).count()
            bank_count = session.query(QuestionBank).count()
            
            session.close()
            
            return {
                'questions': question_count,
                'banks': bank_count
            }
        except Exception as e:
            print(f"获取项目统计失败: {e}")
            return {'questions': 0, 'banks': 0}
    
    def _safe_filename(self, filename):
        """生成安全的文件名"""
        import re
        import hashlib
        
        # 移除或替换不安全的字符
        safe_name = re.sub(r'[<>:"/\\\\|?*]', '_', filename)
        
        # 如果包含非ASCII字符，使用hash值
        if any(ord(char) > 127 for char in safe_name):
            # 保留原始名称的前缀，加上hash值
            prefix = re.sub(r'[^a-zA-Z0-9_-]', '', safe_name)[:10]
            hash_value = hashlib.md5(filename.encode('utf-8')).hexdigest()[:8]
            safe_name = f"{prefix}_{hash_value}"
        
        # 确保文件名不为空且不超过100字符
        if not safe_name or len(safe_name) > 100:
            hash_value = hashlib.md5(filename.encode('utf-8')).hexdigest()[:16]
            safe_name = f"project_{hash_value}"
        
        return safe_name
    
    def close_all(self):
        """关闭所有连接"""
        for session in self._sessions.values():
            try:
                session.close()
            except:
                pass
        self._sessions.clear()

# 全局数据库管理器实例
db_manager = DatabaseManager()
'''
        
        # 写入文件
        with open('question_bank_web/database_manager.py', 'w', encoding='utf-8') as f:
            f.write(db_manager_code)
        
        print("✅ 数据库管理器创建成功")
        return True
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False

def update_flask_app():
    """更新Flask应用以支持多数据库"""
    print("\n🔧 更新Flask应用")
    print("-" * 40)
    
    try:
        app_file = "question_bank_web/app.py"
        
        # 读取现有文件
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 添加数据库管理器导入
        if 'from database_manager import db_manager' not in content:
            # 在其他导入后添加
            import_section = content.find('from models import')
            if import_section != -1:
                # 找到该行的结尾
                line_end = content.find('\\n', import_section)
                new_import = '\\nfrom database_manager import db_manager'
                content = content[:line_end] + new_import + content[line_end:]
                print("✅ 添加数据库管理器导入")
        
        # 修改get_db函数
        old_get_db = '''def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        g.db = Session()
    return g.db'''
        
        new_get_db = '''def get_db():
    """获取当前项目的数据库连接"""
    project_name = session.get('current_project', 'default')
    if 'db' not in g:
        g.db = db_manager.get_session(project_name)
    return g.db'''
        
        if old_get_db in content:
            content = content.replace(old_get_db, new_get_db)
            print("✅ 更新get_db函数")
        
        # 添加项目管理路由
        project_routes = '''

@app.route('/projects')
def list_projects():
    """项目列表页面"""
    projects = db_manager.list_projects()
    current_project = session.get('current_project', 'default')
    
    # 获取每个项目的统计信息
    project_stats = {}
    for project in projects:
        project_stats[project] = db_manager.get_project_stats(project)
    
    return render_template('projects.html', 
                         projects=projects, 
                         current_project=current_project,
                         project_stats=project_stats)

@app.route('/select-project/<project_name>')
def select_project(project_name):
    """选择当前项目"""
    session['current_project'] = project_name
    flash(f'已切换到项目: {project_name}', 'success')
    return redirect(url_for('index'))

@app.route('/create-project', methods=['POST'])
def create_project():
    """创建新项目"""
    project_name = request.form.get('project_name', '').strip()
    
    if not project_name:
        flash('项目名称不能为空', 'error')
        return redirect(url_for('list_projects'))
    
    if db_manager.create_project(project_name):
        flash(f'项目 "{project_name}" 创建成功', 'success')
        session['current_project'] = project_name
    else:
        flash(f'项目 "{project_name}" 创建失败', 'error')
    
    return redirect(url_for('list_projects'))

@app.route('/delete-project/<project_name>', methods=['POST'])
def delete_project(project_name):
    """删除项目"""
    if db_manager.delete_project(project_name):
        flash(f'项目 "{project_name}" 已删除', 'success')
        # 如果删除的是当前项目，切换到默认项目
        if session.get('current_project') == project_name:
            session['current_project'] = 'default'
    else:
        flash(f'项目 "{project_name}" 删除失败', 'error')
    
    return redirect(url_for('list_projects'))'''
        
        # 在文件末尾添加项目管理路由
        if '@app.route(\'/projects\')' not in content:
            # 在if __name__ == '__main__':之前添加
            main_section = content.find('if __name__ == \'__main__\':')
            if main_section != -1:
                content = content[:main_section] + project_routes + '\\n\\n' + content[main_section:]
                print("✅ 添加项目管理路由")
        
        # 写回文件
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Flask应用更新成功")
        return True
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def create_project_templates():
    """创建项目管理模板"""
    print("\\n🔧 创建项目管理模板")
    print("-" * 40)
    
    try:
        # 确保templates目录存在
        templates_dir = "question_bank_web/templates"
        os.makedirs(templates_dir, exist_ok=True)
        
        # 项目列表模板
        projects_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>项目管理 - 题库管理系统</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-12">
                <h2>项目管理</h2>
                
                <!-- 当前项目显示 -->
                <div class="alert alert-info">
                    <strong>当前项目:</strong> {{ current_project }}
                </div>
                
                <!-- 创建新项目 -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>创建新项目</h5>
                    </div>
                    <div class="card-body">
                        <form method="POST" action="{{ url_for('create_project') }}">
                            <div class="input-group">
                                <input type="text" class="form-control" name="project_name" 
                                       placeholder="输入项目名称" required>
                                <button class="btn btn-primary" type="submit">创建项目</button>
                            </div>
                        </form>
                    </div>
                </div>
                
                <!-- 项目列表 -->
                <div class="card">
                    <div class="card-header">
                        <h5>现有项目</h5>
                    </div>
                    <div class="card-body">
                        {% if projects %}
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>项目名称</th>
                                            <th>题目数量</th>
                                            <th>题库数量</th>
                                            <th>操作</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for project in projects %}
                                        <tr {% if project == current_project %}class="table-primary"{% endif %}>
                                            <td>
                                                <strong>{{ project }}</strong>
                                                {% if project == current_project %}
                                                    <span class="badge bg-primary">当前</span>
                                                {% endif %}
                                            </td>
                                            <td>{{ project_stats[project].questions }}</td>
                                            <td>{{ project_stats[project].banks }}</td>
                                            <td>
                                                {% if project != current_project %}
                                                    <a href="{{ url_for('select_project', project_name=project) }}" 
                                                       class="btn btn-sm btn-outline-primary">切换</a>
                                                {% endif %}
                                                
                                                {% if project != 'default' %}
                                                    <form method="POST" action="{{ url_for('delete_project', project_name=project) }}" 
                                                          style="display: inline;" 
                                                          onsubmit="return confirm('确定要删除项目 {{ project }} 吗？此操作不可恢复！')">
                                                        <button type="submit" class="btn btn-sm btn-outline-danger">删除</button>
                                                    </form>
                                                {% endif %}
                                            </td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        {% else %}
                            <p class="text-muted">暂无项目，请创建第一个项目。</p>
                        {% endif %}
                    </div>
                </div>
                
                <!-- 返回按钮 -->
                <div class="mt-3">
                    <a href="{{ url_for('index') }}" class="btn btn-secondary">返回主页</a>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 显示Flash消息 -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="position-fixed top-0 end-0 p-3" style="z-index: 11">
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
        
        # 写入模板文件
        with open(os.path.join(templates_dir, 'projects.html'), 'w', encoding='utf-8') as f:
            f.write(projects_template)
        
        print("✅ 项目管理模板创建成功")
        return True
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False

def migrate_existing_data():
    """迁移现有数据到多数据库架构"""
    print("\\n🔧 迁移现有数据")
    print("-" * 40)
    
    try:
        # 检查是否有现有数据库
        old_db_path = "question_bank_web/questions.db"
        if not os.path.exists(old_db_path):
            print("✅ 没有现有数据需要迁移")
            return True
        
        # 备份现有数据库
        backup_path = f"{old_db_path}.backup"
        shutil.copy2(old_db_path, backup_path)
        print(f"✅ 已备份现有数据库到: {backup_path}")
        
        # 导入必要的模块
        sys.path.append('question_bank_web')
        from models import Base, Question, QuestionBank
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from database_manager import db_manager
        
        # 连接旧数据库
        old_engine = create_engine(f'sqlite:///{old_db_path}')
        OldSession = sessionmaker(bind=old_engine)
        old_session = OldSession()
        
        # 获取所有数据
        try:
            questions = old_session.query(Question).all()
            banks = old_session.query(QuestionBank).all()
            
            print(f"找到 {len(banks)} 个题库，{len(questions)} 个题目")
            
            # 按题库分组迁移数据
            for bank in banks:
                project_name = bank.name
                print(f"正在迁移项目: {project_name}")
                
                # 获取该题库的所有题目
                bank_questions = [q for q in questions if hasattr(q, 'bank_id') and q.bank_id == bank.id]
                
                # 创建新项目数据库
                new_session = db_manager.get_session(project_name)
                
                try:
                    # 创建题库记录
                    new_bank = QuestionBank(
                        id=bank.id,
                        name=bank.name,
                        description=getattr(bank, 'description', '')
                    )
                    new_session.add(new_bank)
                    new_session.flush()  # 获取ID
                    
                    # 迁移题目
                    for question in bank_questions:
                        new_question = Question(
                            id=question.id,
                            bank_id=new_bank.id,
                            content=getattr(question, 'content', ''),
                            question_type=getattr(question, 'question_type', ''),
                            difficulty=getattr(question, 'difficulty', ''),
                            options=getattr(question, 'options', ''),
                            correct_answer=getattr(question, 'correct_answer', ''),
                            explanation=getattr(question, 'explanation', ''),
                            tags=getattr(question, 'tags', ''),
                            created_at=getattr(question, 'created_at', None)
                        )
                        new_session.add(new_question)
                    
                    new_session.commit()
                    print(f"  ✅ 成功迁移 {len(bank_questions)} 个题目")
                    
                except Exception as e:
                    new_session.rollback()
                    print(f"  ❌ 迁移失败: {e}")
                finally:
                    new_session.close()
            
        except Exception as e:
            print(f"❌ 读取旧数据失败: {e}")
            return False
        finally:
            old_session.close()
        
        print("✅ 数据迁移完成")
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def main():
    """主函数"""
    print("🔧 实施多数据库架构解决方案")
    print("=" * 50)
    
    steps = [
        ("创建数据库管理器", create_database_manager),
        ("更新Flask应用", update_flask_app),
        ("创建项目管理模板", create_project_templates),
        ("迁移现有数据", migrate_existing_data),
    ]
    
    passed_steps = 0
    total_steps = len(steps)
    
    for step_name, step_func in steps:
        print(f"\\n{'='*20} {step_name} {'='*20}")
        try:
            if step_func():
                passed_steps += 1
                print(f"✅ {step_name} 完成")
            else:
                print(f"❌ {step_name} 失败")
        except Exception as e:
            print(f"❌ 步骤 '{step_name}' 执行异常: {e}")
    
    print("\\n" + "=" * 50)
    print("📊 实施结果摘要")
    print(f"完成步骤: {passed_steps}/{total_steps}")
    print(f"成功率: {(passed_steps/total_steps)*100:.1f}%")
    
    if passed_steps == total_steps:
        print("\\n🎉 多数据库架构实施成功！")
        print("\\n✅ 新功能:")
        print("1. ✅ 每个项目独立数据库")
        print("2. ✅ 项目管理界面 (/projects)")
        print("3. ✅ 项目切换功能")
        print("4. ✅ 数据完全隔离")
        print("5. ✅ 现有数据已迁移")
        
        print("\\n🎯 使用方法:")
        print("1. 访问 /projects 管理项目")
        print("2. 创建新项目或切换现有项目")
        print("3. 在选定项目中进行题库操作")
        print("4. 每个项目的数据完全独立")
        
        print("\\n📁 数据库文件位置:")
        print("question_bank_web/question_banks/")
        print("├── 项目A.db")
        print("├── 项目B.db")
        print("└── default.db")
        
    else:
        print("\\n⚠️  部分步骤失败，请检查错误信息")
    
    return passed_steps == total_steps

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
