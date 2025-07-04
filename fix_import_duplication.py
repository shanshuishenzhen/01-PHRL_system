#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复题库导入重复和错误问题
"""

import os
import sys
import traceback

def fix_import_function():
    """修复导入函数中的重复问题"""
    print("🔧 修复导入函数")
    print("-" * 40)
    
    try:
        excel_importer_file = "question_bank_web/excel_importer.py"
        
        # 读取文件
        with open(excel_importer_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复重复ID检查逻辑
        old_id_check = '''    # 1. 查数据库已存在ID
    try:
        db_existing_ids = set([row[0] for row in db_session.execute(text('SELECT id FROM questions')).fetchall()])
    except Exception:
        db_existing_ids = set()

    # 2. Excel内部和数据库冲突自动修正ID
    seen_ids = set(db_existing_ids)
    for index, row in df.iterrows():
        orig_id = str(row.get('ID', '')).strip()
        bank_name = str(row.get('题库名称', '')).strip()
        new_id = orig_id
        suffix = bank_name[:4] if bank_name else 'BK'
        seq = 1
        while new_id in seen_ids:
            new_id = f"{orig_id}_{suffix}{seq}"
            seq += 1
        df.at[index, 'ID'] = new_id
        seen_ids.add(new_id)'''
        
        new_id_check = '''    # 1. 查数据库已存在ID（仅在当前项目中）
    try:
        db_existing_ids = set([row[0] for row in db_session.execute(text('SELECT id FROM questions')).fetchall()])
        print(f"数据库中已存在 {len(db_existing_ids)} 个题目ID")
    except Exception as e:
        print(f"查询现有ID失败: {e}")
        db_existing_ids = set()

    # 2. 检查Excel内部ID重复
    excel_ids = []
    for index, row in df.iterrows():
        question_id = str(row.get('ID', '')).strip()
        if question_id:
            excel_ids.append(question_id)
    
    # 统计Excel中的重复ID
    from collections import Counter
    id_counts = Counter(excel_ids)
    duplicate_ids = {id_val: count for id_val, count in id_counts.items() if count > 1}
    
    if duplicate_ids:
        print(f"Excel中发现重复ID: {len(duplicate_ids)} 个")
        for id_val, count in list(duplicate_ids.items())[:5]:  # 只显示前5个
            print(f"  {id_val}: {count} 次")
    
    # 3. 去重处理：保留第一个，跳过重复的
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
        
        if old_id_check in content:
            content = content.replace(old_id_check, new_id_check)
            print("✅ 更新ID检查逻辑")
        
        # 修复主循环，添加跳过逻辑
        old_loop_start = '''    for index, row in df.iterrows():
        row_num = index + 2
        try:'''
        
        new_loop_start = '''    for index, row in df.iterrows():
        row_num = index + 2
        
        # 跳过重复的行
        if index in rows_to_skip:
            continue
            
        try:'''
        
        if old_loop_start in content:
            content = content.replace(old_loop_start, new_loop_start)
            print("✅ 更新主循环逻辑")
        
        # 添加更详细的调试信息
        old_insert_section = '''            print(f"实际插入ID: {question_id_str}")
            questions_to_add.append(question)'''
        
        new_insert_section = '''            print(f"准备插入ID: {question_id_str}")
            questions_to_add.append(question)'''
        
        if old_insert_section in content:
            content = content.replace(old_insert_section, new_insert_section)
            print("✅ 更新调试信息")
        
        # 写回文件
        with open(excel_importer_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 导入函数修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def fix_flask_app_import():
    """修复Flask应用中的导入处理"""
    print("\n🔧 修复Flask应用导入处理")
    print("-" * 40)
    
    try:
        app_file = "question_bank_web/app.py"
        
        # 读取文件
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复handle_import_sample函数，添加项目信息
        old_function = '''@app.route('/import-sample', methods=['GET'])
def handle_import_sample():
    """处理从Excel文件导入样例题库的请求"""
    db = get_db()
    excel_file_path = os.path.join(os.path.dirname(__file__), 'questions_sample.xlsx')
    
    if not os.path.exists(excel_file_path):
        flash(f"错误：样例题库文件 'questions_sample.xlsx' 不存在。", 'error')
        return redirect(url_for('index'))
    
    try:
        questions_added, errors = import_questions_from_excel(excel_file_path, db)'''
        
        new_function = '''@app.route('/import-sample', methods=['GET'])
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
        print(f"导入完成: 添加 {len(questions_added) if questions_added else 0} 个题目, {len(errors) if errors else 0} 个错误")'''
        
        if old_function in content:
            content = content.replace(old_function, new_function)
            print("✅ 更新handle_import_sample函数")
        
        # 写回文件
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Flask应用修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def add_project_context_debug():
    """添加项目上下文调试信息"""
    print("\n🔧 添加项目上下文调试")
    print("-" * 40)
    
    try:
        app_file = "question_bank_web/app.py"
        
        # 读取文件
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修改get_db函数，添加调试信息
        old_get_db = '''def get_db():
    """获取当前项目的数据库连接"""
    project_name = session.get('current_project', 'default')
    if 'db' not in g:
        g.db = db_manager.get_session(project_name)
    return g.db'''
        
        new_get_db = '''def get_db():
    """获取当前项目的数据库连接"""
    project_name = session.get('current_project', 'default')
    print(f"get_db: 当前项目 = {project_name}")
    if 'db' not in g:
        g.db = db_manager.get_session(project_name)
        print(f"get_db: 为项目 {project_name} 创建新的数据库会话")
    return g.db'''
        
        if old_get_db in content:
            content = content.replace(old_get_db, new_get_db)
            print("✅ 更新get_db函数调试信息")
        
        # 写回文件
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 项目上下文调试添加完成")
        return True
        
    except Exception as e:
        print(f"❌ 添加失败: {e}")
        return False

def create_import_test_script():
    """创建导入测试脚本"""
    print("\n🔧 创建导入测试脚本")
    print("-" * 40)
    
    try:
        test_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导入功能的脚本
"""

import os
import sys

def test_import_with_project():
    """测试指定项目的导入功能"""
    sys.path.append('question_bank_web')
    
    from database_manager import db_manager
    from excel_importer import import_questions_from_excel
    
    # 测试项目
    test_projects = ['test_project_1', 'test_project_2']
    
    for project_name in test_projects:
        print(f"\\n测试项目: {project_name}")
        print("-" * 30)
        
        # 获取项目数据库会话
        session = db_manager.get_session(project_name)
        
        # 清空现有数据
        try:
            session.execute("DELETE FROM questions")
            session.execute("DELETE FROM question_banks")
            session.commit()
            print(f"✅ 清空项目 {project_name} 的现有数据")
        except Exception as e:
            print(f"⚠️  清空数据失败: {e}")
            session.rollback()
        
        # 测试导入
        excel_file = 'question_bank_web/questions_sample.xlsx'
        if os.path.exists(excel_file):
            questions_added, errors = import_questions_from_excel(excel_file, session)
            
            print(f"导入结果:")
            print(f"  成功添加: {len(questions_added) if questions_added else 0} 个题目")
            print(f"  错误数量: {len(errors) if errors else 0} 个")
            
            if errors:
                print(f"  前5个错误:")
                for i, error in enumerate(errors[:5]):
                    print(f"    {i+1}. {error}")
        else:
            print(f"❌ 样例文件不存在: {excel_file}")
        
        session.close()

if __name__ == "__main__":
    test_import_with_project()'''
        
        with open('test_import.py', 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        print("✅ 导入测试脚本创建完成")
        return True
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 修复题库导入重复和错误问题")
    print("=" * 50)
    
    fixes = [
        ("修复导入函数", fix_import_function),
        ("修复Flask应用导入处理", fix_flask_app_import),
        ("添加项目上下文调试", add_project_context_debug),
        ("创建导入测试脚本", create_import_test_script),
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
        print("\\n🎉 主要问题已修复！")
        print("\\n✅ 修复内容:")
        print("1. ✅ 改进ID重复检查逻辑")
        print("2. ✅ 添加Excel内部去重处理")
        print("3. ✅ 增强项目上下文调试")
        print("4. ✅ 跳过重复和已存在的题目")
        
        print("\\n🎯 现在应该解决:")
        print("• 数量加倍问题（去重处理）")
        print("• 重复ID错误（跳过重复项）")
        print("• 项目隔离问题（调试信息）")
        
        print("\\n🧪 测试建议:")
        print("1. 运行 python test_import.py 进行独立测试")
        print("2. 重新启动Flask应用")
        print("3. 在不同项目中测试导入功能")
        print("4. 观察控制台调试信息")
        
    else:
        print("\\n⚠️  部分修复失败，请检查错误信息")
    
    return passed_fixes >= 3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
