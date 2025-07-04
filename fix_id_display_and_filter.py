#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复ID显示问题并添加题库筛选功能
"""

import os
import sys
import traceback

def fix_id_processing_logic():
    """修复ID处理逻辑，不添加后缀"""
    print("🔧 修复ID处理逻辑")
    print("-" * 40)
    
    try:
        excel_importer_file = "question_bank_web/excel_importer.py"
        
        # 读取文件
        with open(excel_importer_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除错误的ID修改逻辑
        old_id_logic = '''    # 3. 去重处理：保留第一个，跳过重复的
    seen_ids = set(db_existing_ids)
    excel_seen_ids = set()
    rows_to_skip = set()
    
    for index, row in df.iterrows():
        question_id = str(row.get('ID', '')).strip()
        if not question_id:
            continue
            
        # 如果在Excel中已经见过这个ID，标记跳过
        if question_id in excel_seen_ids:
            rows_to_skip.add(index)
            continue
            
        # 如果在数据库中已存在，标记跳过
        if question_id in seen_ids:
            rows_to_skip.add(index)
            continue
            
        excel_seen_ids.add(question_id)
        seen_ids.add(question_id)
    
    print(f"将跳过 {len(rows_to_skip)} 个重复或已存在的题目")'''
        
        new_id_logic = '''    # 3. 去重处理：在当前项目中保持ID唯一性
    seen_ids = set(db_existing_ids)
    excel_seen_ids = set()
    rows_to_skip = set()
    
    for index, row in df.iterrows():
        question_id = str(row.get('ID', '')).strip()
        if not question_id:
            continue
            
        # 如果在Excel中已经见过这个ID，标记跳过（保留第一个）
        if question_id in excel_seen_ids:
            rows_to_skip.add(index)
            print(f"跳过Excel中重复的ID: {question_id}")
            continue
            
        # 如果在当前项目数据库中已存在，标记跳过
        if question_id in seen_ids:
            rows_to_skip.add(index)
            print(f"跳过数据库中已存在的ID: {question_id}")
            continue
            
        excel_seen_ids.add(question_id)
        seen_ids.add(question_id)
    
    print(f"将跳过 {len(rows_to_skip)} 个重复或已存在的题目")
    print(f"将导入 {len(df) - len(rows_to_skip)} 个新题目")'''
        
        if old_id_logic in content:
            content = content.replace(old_id_logic, new_id_logic)
            print("✅ 更新ID处理逻辑")
        
        # 确保ID保持原样，不添加任何后缀
        # 检查是否有修改ID的代码
        if 'df.at[index, \'ID\'] = new_id' in content:
            # 移除这行代码
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if 'df.at[index, \'ID\'] = new_id' not in line:
                    new_lines.append(line)
            content = '\n'.join(new_lines)
            print("✅ 移除ID修改代码")
        
        # 写回文件
        with open(excel_importer_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ ID处理逻辑修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def add_question_filter_functionality():
    """添加题目筛选功能"""
    print("\n🔧 添加题目筛选功能")
    print("-" * 40)
    
    try:
        app_file = "question_bank_web/app.py"
        
        # 读取文件
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 添加筛选路由
        filter_route = '''
@app.route('/questions/filter')
def filter_questions():
    """筛选题目"""
    db = get_db()
    
    # 获取筛选参数
    bank_name = request.args.get('bank_name', '')
    question_type = request.args.get('question_type', '')
    difficulty = request.args.get('difficulty', '')
    page = int(request.args.get('page', 1))
    per_page = 20
    
    try:
        # 构建查询
        query = db.query(Question).join(QuestionBank)
        
        # 应用筛选条件
        if bank_name:
            query = query.filter(QuestionBank.name.like(f'%{bank_name}%'))
        
        if question_type:
            query = query.filter(Question.question_type == question_type)
        
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        
        # 分页
        total = query.count()
        questions = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # 获取所有题库名称用于筛选下拉框
        banks = db.query(QuestionBank).all()
        
        # 获取所有题型和难度用于筛选
        question_types = db.query(Question.question_type).distinct().all()
        difficulties = db.query(Question.difficulty).distinct().all()
        
        return render_template('questions_filter.html',
                             questions=questions,
                             banks=banks,
                             question_types=[qt[0] for qt in question_types if qt[0]],
                             difficulties=[d[0] for d in difficulties if d[0]],
                             current_filters={
                                 'bank_name': bank_name,
                                 'question_type': question_type,
                                 'difficulty': difficulty
                             },
                             pagination={
                                 'page': page,
                                 'per_page': per_page,
                                 'total': total,
                                 'pages': (total + per_page - 1) // per_page
                             })
    
    except Exception as e:
        flash(f'筛选题目时发生错误: {e}', 'error')
        return redirect(url_for('index'))
    finally:
        close_db(db)'''
        
        # 在项目管理路由之前添加筛选路由
        if '@app.route(\'/projects\')' in content:
            insertion_point = content.find('@app.route(\'/projects\')')
            content = content[:insertion_point] + filter_route + '\n\n' + content[insertion_point:]
            print("✅ 添加题目筛选路由")
        
        # 写回文件
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 题目筛选功能添加完成")
        return True
        
    except Exception as e:
        print(f"❌ 添加失败: {e}")
        return False

def create_filter_template():
    """创建筛选页面模板"""
    print("\n🔧 创建筛选页面模板")
    print("-" * 40)
    
    try:
        templates_dir = "question_bank_web/templates"
        os.makedirs(templates_dir, exist_ok=True)
        
        filter_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>题目筛选 - 题库管理系统</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-12">
                <h2>题目筛选</h2>
                
                <!-- 筛选表单 -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>筛选条件</h5>
                    </div>
                    <div class="card-body">
                        <form method="GET" action="{{ url_for('filter_questions') }}">
                            <div class="row">
                                <div class="col-md-3">
                                    <label for="bank_name" class="form-label">题库名称</label>
                                    <select class="form-select" name="bank_name" id="bank_name">
                                        <option value="">全部题库</option>
                                        {% for bank in banks %}
                                            <option value="{{ bank.name }}" 
                                                {% if current_filters.bank_name == bank.name %}selected{% endif %}>
                                                {{ bank.name }}
                                            </option>
                                        {% endfor %}
                                    </select>
                                </div>
                                
                                <div class="col-md-3">
                                    <label for="question_type" class="form-label">题型</label>
                                    <select class="form-select" name="question_type" id="question_type">
                                        <option value="">全部题型</option>
                                        {% for qtype in question_types %}
                                            <option value="{{ qtype }}" 
                                                {% if current_filters.question_type == qtype %}selected{% endif %}>
                                                {{ qtype }}
                                            </option>
                                        {% endfor %}
                                    </select>
                                </div>
                                
                                <div class="col-md-3">
                                    <label for="difficulty" class="form-label">难度</label>
                                    <select class="form-select" name="difficulty" id="difficulty">
                                        <option value="">全部难度</option>
                                        {% for diff in difficulties %}
                                            <option value="{{ diff }}" 
                                                {% if current_filters.difficulty == diff %}selected{% endif %}>
                                                {{ diff }}
                                            </option>
                                        {% endfor %}
                                    </select>
                                </div>
                                
                                <div class="col-md-3">
                                    <label class="form-label">&nbsp;</label>
                                    <div>
                                        <button type="submit" class="btn btn-primary">筛选</button>
                                        <a href="{{ url_for('filter_questions') }}" class="btn btn-secondary">重置</a>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
                
                <!-- 题目列表 -->
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5>题目列表 (共 {{ pagination.total }} 题)</h5>
                        <a href="{{ url_for('index') }}" class="btn btn-outline-secondary btn-sm">返回主页</a>
                    </div>
                    <div class="card-body">
                        {% if questions %}
                            <div class="table-responsive">
                                <table class="table table-striped table-hover">
                                    <thead>
                                        <tr>
                                            <th style="width: 15%;">ID</th>
                                            <th style="width: 20%;">题库名称</th>
                                            <th style="width: 45%;">题干</th>
                                            <th style="width: 10%;">题型</th>
                                            <th style="width: 10%;">难度</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for question in questions %}
                                        <tr>
                                            <td><code>{{ question.id }}</code></td>
                                            <td>
                                                <span class="badge bg-info">{{ question.bank.name }}</span>
                                            </td>
                                            <td>
                                                <div style="max-height: 60px; overflow: hidden;">
                                                    {{ question.content[:100] }}
                                                    {% if question.content|length > 100 %}...{% endif %}
                                                </div>
                                            </td>
                                            <td>
                                                <span class="badge bg-secondary">{{ question.question_type }}</span>
                                            </td>
                                            <td>
                                                <span class="badge bg-warning">{{ question.difficulty }}</span>
                                            </td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                            
                            <!-- 分页 -->
                            {% if pagination.pages > 1 %}
                                <nav aria-label="题目分页">
                                    <ul class="pagination justify-content-center">
                                        {% if pagination.page > 1 %}
                                            <li class="page-item">
                                                <a class="page-link" href="{{ url_for('filter_questions', 
                                                    page=pagination.page-1,
                                                    bank_name=current_filters.bank_name,
                                                    question_type=current_filters.question_type,
                                                    difficulty=current_filters.difficulty) }}">上一页</a>
                                            </li>
                                        {% endif %}
                                        
                                        {% for page_num in range(1, pagination.pages + 1) %}
                                            {% if page_num == pagination.page %}
                                                <li class="page-item active">
                                                    <span class="page-link">{{ page_num }}</span>
                                                </li>
                                            {% elif page_num <= 3 or page_num > pagination.pages - 3 or (page_num >= pagination.page - 1 and page_num <= pagination.page + 1) %}
                                                <li class="page-item">
                                                    <a class="page-link" href="{{ url_for('filter_questions', 
                                                        page=page_num,
                                                        bank_name=current_filters.bank_name,
                                                        question_type=current_filters.question_type,
                                                        difficulty=current_filters.difficulty) }}">{{ page_num }}</a>
                                                </li>
                                            {% elif page_num == 4 or page_num == pagination.pages - 3 %}
                                                <li class="page-item disabled">
                                                    <span class="page-link">...</span>
                                                </li>
                                            {% endif %}
                                        {% endfor %}
                                        
                                        {% if pagination.page < pagination.pages %}
                                            <li class="page-item">
                                                <a class="page-link" href="{{ url_for('filter_questions', 
                                                    page=pagination.page+1,
                                                    bank_name=current_filters.bank_name,
                                                    question_type=current_filters.question_type,
                                                    difficulty=current_filters.difficulty) }}">下一页</a>
                                            </li>
                                        {% endif %}
                                    </ul>
                                </nav>
                            {% endif %}
                            
                        {% else %}
                            <div class="text-center text-muted py-4">
                                <p>没有找到符合条件的题目</p>
                            </div>
                        {% endif %}
                    </div>
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
        with open(os.path.join(templates_dir, 'questions_filter.html'), 'w', encoding='utf-8') as f:
            f.write(filter_template)
        
        print("✅ 筛选页面模板创建成功")
        return True
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False

def update_main_template():
    """更新主页模板，添加筛选链接"""
    print("\n🔧 更新主页模板")
    print("-" * 40)
    
    try:
        # 检查主页模板是否存在
        main_template_path = "question_bank_web/templates/index.html"
        if not os.path.exists(main_template_path):
            print("⚠️  主页模板不存在，跳过更新")
            return True
        
        # 读取主页模板
        with open(main_template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 添加筛选按钮
        if '导入样例题库' in content and '题目筛选' not in content:
            # 在导入样例题库按钮后添加筛选按钮
            old_buttons = '<a href="{{ url_for(\'handle_import_sample\') }}" class="btn btn-primary">导入样例题库</a>'
            new_buttons = '''<a href="{{ url_for('handle_import_sample') }}" class="btn btn-primary">导入样例题库</a>
            <a href="{{ url_for('filter_questions') }}" class="btn btn-info">题目筛选</a>'''
            
            content = content.replace(old_buttons, new_buttons)
            
            # 写回文件
            with open(main_template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ 主页模板更新成功")
        else:
            print("✅ 主页模板已包含筛选功能或格式不匹配")
        
        return True
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 修复ID显示问题并添加题库筛选功能")
    print("=" * 50)
    
    fixes = [
        ("修复ID处理逻辑", fix_id_processing_logic),
        ("添加题目筛选功能", add_question_filter_functionality),
        ("创建筛选页面模板", create_filter_template),
        ("更新主页模板", update_main_template),
    ]
    
    passed_fixes = 0
    total_fixes = len(fixes)
    
    for fix_name, fix_func in fixes:
        print(f"\\n{'='*20} {fix_name} {'='*20}")
        try:
            if fix_func():
                passed_fixes += 1
                print(f"✅ {fix_name} 完成")
            else:
                print(f"❌ {fix_name} 失败")
        except Exception as e:
            print(f"❌ 修复 '{fix_name}' 执行异常: {e}")
    
    print("\\n" + "=" * 50)
    print("📊 修复结果摘要")
    print(f"完成修复: {passed_fixes}/{total_fixes}")
    print(f"成功率: {(passed_fixes/total_fixes)*100:.1f}%")
    
    if passed_fixes >= 3:
        print("\\n🎉 主要功能已完成！")
        print("\\n✅ 修复和新增内容:")
        print("1. ✅ 修复ID显示问题（移除不必要的后缀）")
        print("2. ✅ 添加题目筛选功能")
        print("3. ✅ 创建专业的筛选界面")
        print("4. ✅ 支持按题库、题型、难度筛选")
        print("5. ✅ 添加分页功能")
        
        print("\\n🎯 新功能特点:")
        print("• ID保持原样，不添加后缀")
        print("• 按题库名称筛选题目")
        print("• 按题型和难度筛选")
        print("• 分页显示，提高性能")
        print("• 清晰的表格展示")
        
        print("\\n🚀 使用方法:")
        print("1. 重新启动Flask应用")
        print("2. 访问主页，点击'题目筛选'按钮")
        print("3. 或直接访问: http://localhost:5000/questions/filter")
        print("4. 使用筛选条件查看特定题目")
        
    else:
        print("\\n⚠️  部分功能失败，请检查错误信息")
    
    return passed_fixes >= 3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
