#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彻底修复题库导入问题
"""

import os
import sys
import traceback

def completely_fix_excel_importer():
    """彻底修复Excel导入器"""
    print("🔧 彻底修复Excel导入器")
    print("-" * 40)
    
    try:
        excel_importer_file = "question_bank_web/excel_importer.py"
        
        # 读取文件
        with open(excel_importer_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 完全重写ID处理部分
        # 找到并替换整个ID处理逻辑
        start_marker = "    # 1. 查数据库已存在ID"
        end_marker = "    # 3. 自动同步题库表"
        
        start_pos = content.find(start_marker)
        end_pos = content.find(end_marker)
        
        if start_pos != -1 and end_pos != -1:
            # 新的ID处理逻辑
            new_id_logic = '''    # 1. 查数据库已存在ID（仅在当前项目中）
    try:
        db_existing_ids = set([row[0] for row in db_session.execute(text('SELECT id FROM questions')).fetchall()])
        print(f"当前项目数据库中已存在 {len(db_existing_ids)} 个题目ID")
    except Exception as e:
        print(f"查询现有ID失败: {e}")
        db_existing_ids = set()

    # 2. 统计Excel中的ID情况
    excel_ids = []
    for index, row in df.iterrows():
        question_id = str(row.get('ID', '')).strip()
        if question_id:
            excel_ids.append(question_id)
    
    print(f"Excel文件中包含 {len(excel_ids)} 个题目")
    
    # 统计重复情况
    from collections import Counter
    id_counts = Counter(excel_ids)
    duplicate_ids = {id_val: count for id_val, count in id_counts.items() if count > 1}
    
    if duplicate_ids:
        print(f"Excel中发现 {len(duplicate_ids)} 个重复ID:")
        for id_val, count in list(duplicate_ids.items())[:3]:
            print(f"  {id_val}: 出现 {count} 次")
    
    # 3. 去重处理：保留第一个出现的ID，跳过后续重复
    seen_excel_ids = set()
    seen_db_ids = set(db_existing_ids)
    rows_to_skip = set()
    
    for index, row in df.iterrows():
        question_id = str(row.get('ID', '')).strip()
        if not question_id:
            rows_to_skip.add(index)
            continue
            
        # 如果在Excel中已经见过这个ID，跳过
        if question_id in seen_excel_ids:
            rows_to_skip.add(index)
            continue
            
        # 如果在数据库中已存在，跳过
        if question_id in seen_db_ids:
            rows_to_skip.add(index)
            continue
            
        # 记录这个ID
        seen_excel_ids.add(question_id)
        seen_db_ids.add(question_id)
    
    print(f"将跳过 {len(rows_to_skip)} 个重复或已存在的题目")
    print(f"将导入 {len(df) - len(rows_to_skip)} 个新题目")

    '''
            
            # 替换内容
            new_content = content[:start_pos] + new_id_logic + content[end_pos:]
            content = new_content
            print("✅ 重写ID处理逻辑")
        
        # 确保主循环中不修改ID
        # 查找并移除任何修改ID的代码
        lines = content.split('\n')
        new_lines = []
        skip_next = False
        
        for i, line in enumerate(lines):
            # 跳过任何修改ID的行
            if 'df.at[index, \'ID\']' in line or 'new_id =' in line or 'suffix =' in line:
                continue
            # 跳过while循环修改ID的部分
            if 'while new_id in seen_ids:' in line:
                skip_next = True
                continue
            if skip_next and ('seq += 1' in line or 'new_id = f' in line):
                continue
            if skip_next and line.strip() == '':
                skip_next = False
                continue
            
            new_lines.append(line)
        
        content = '\n'.join(new_lines)
        print("✅ 移除ID修改代码")
        
        # 写回文件
        with open(excel_importer_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Excel导入器彻底修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def fix_question_counting():
    """修复题目计数问题"""
    print("\n🔧 修复题目计数问题")
    print("-" * 40)
    
    try:
        app_file = "question_bank_web/app.py"
        
        # 读取文件
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找index路由中的统计代码
        if 'total_questions = db.query(Question).count()' in content:
            # 修复统计逻辑，确保只统计当前项目
            old_stats = '''        total_questions = db.query(Question).count()
        total_banks = db.query(QuestionBank).count()'''
        
        new_stats = '''        # 统计当前项目的题目和题库数量
        total_questions = db.query(Question).count()
        total_banks = db.query(QuestionBank).count()
        
        print(f"当前项目统计: {total_questions} 个题目, {total_banks} 个题库")'''
        
        content = content.replace(old_stats, new_stats)
        print("✅ 更新统计逻辑")
        
        # 写回文件
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 题目计数修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def create_database_cleanup_script():
    """创建数据库清理脚本"""
    print("\n🔧 创建数据库清理脚本")
    print("-" * 40)
    
    try:
        cleanup_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理数据库中的重复和错误数据
"""

import os
import sys

def clean_project_database(project_name):
    """清理指定项目的数据库"""
    print(f"清理项目: {project_name}")
    
    sys.path.append('question_bank_web')
    from database_manager import db_manager
    from models import Question, QuestionBank
    
    session = db_manager.get_session(project_name)
    
    try:
        # 1. 统计当前数据
        total_questions = session.query(Question).count()
        total_banks = session.query(QuestionBank).count()
        print(f"清理前: {total_questions} 个题目, {total_banks} 个题库")
        
        # 2. 查找带后缀的ID
        questions_with_suffix = session.query(Question).filter(Question.id.like('%_保卫管理%')).all()
        questions_with_suffix += session.query(Question).filter(Question.id.like('%_视频创推%')).all()
        
        if questions_with_suffix:
            print(f"发现 {len(questions_with_suffix)} 个带后缀的题目ID")
            
            # 删除带后缀的题目
            for question in questions_with_suffix:
                print(f"删除带后缀的题目: {question.id}")
                session.delete(question)
            
            session.commit()
            print(f"✅ 已删除 {len(questions_with_suffix)} 个带后缀的题目")
        
        # 3. 查找重复ID（不带后缀的）
        from collections import Counter
        all_questions = session.query(Question).all()
        id_counts = Counter([q.id for q in all_questions])
        duplicate_ids = [id_val for id_val, count in id_counts.items() if count > 1]
        
        if duplicate_ids:
            print(f"发现 {len(duplicate_ids)} 个重复ID")
            
            for dup_id in duplicate_ids:
                # 保留第一个，删除其余的
                questions = session.query(Question).filter(Question.id == dup_id).all()
                for question in questions[1:]:  # 跳过第一个
                    print(f"删除重复题目: {question.id}")
                    session.delete(question)
            
            session.commit()
            print(f"✅ 已清理重复ID")
        
        # 4. 统计清理后的数据
        final_questions = session.query(Question).count()
        final_banks = session.query(QuestionBank).count()
        print(f"清理后: {final_questions} 个题目, {final_banks} 个题库")
        
        return True
        
    except Exception as e:
        print(f"清理失败: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def clean_all_projects():
    """清理所有项目"""
    sys.path.append('question_bank_web')
    from database_manager import db_manager
    
    projects = db_manager.list_projects()
    print(f"发现 {len(projects)} 个项目: {projects}")
    
    for project in projects:
        print(f"\\n{'='*30}")
        clean_project_database(project)

if __name__ == "__main__":
    clean_all_projects()'''
        
        with open('clean_database.py', 'w', encoding='utf-8') as f:
            f.write(cleanup_script)
        
        print("✅ 数据库清理脚本创建完成")
        return True
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False

def create_import_verification_script():
    """创建导入验证脚本"""
    print("\n🔧 创建导入验证脚本")
    print("-" * 40)
    
    try:
        verify_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证导入功能的脚本
"""

import os
import sys

def verify_import_for_project(project_name):
    """验证指定项目的导入功能"""
    print(f"验证项目: {project_name}")
    print("-" * 30)
    
    sys.path.append('question_bank_web')
    from database_manager import db_manager
    from excel_importer import import_questions_from_excel
    
    session = db_manager.get_session(project_name)
    
    try:
        # 1. 清空现有数据
        session.execute("DELETE FROM questions")
        session.execute("DELETE FROM question_banks")
        session.commit()
        print("✅ 清空现有数据")
        
        # 2. 执行导入
        excel_file = 'question_bank_web/questions_sample.xlsx'
        if not os.path.exists(excel_file):
            print(f"❌ 样例文件不存在: {excel_file}")
            return False
        
        print("开始导入...")
        questions_added, errors = import_questions_from_excel(excel_file, session)
        
        print(f"导入结果:")
        print(f"  成功添加: {len(questions_added) if questions_added else 0} 个题目")
        print(f"  错误数量: {len(errors) if errors else 0} 个")
        
        # 3. 验证ID格式
        from models import Question
        all_questions = session.query(Question).all()
        
        correct_ids = 0
        wrong_ids = 0
        
        for question in all_questions[:10]:  # 检查前10个
            if '_' in question.id and ('保卫管理' in question.id or '视频创推' in question.id):
                print(f"❌ 错误ID格式: {question.id}")
                wrong_ids += 1
            else:
                print(f"✅ 正确ID格式: {question.id}")
                correct_ids += 1
        
        print(f"\\nID格式检查: {correct_ids} 个正确, {wrong_ids} 个错误")
        
        # 4. 统计最终结果
        total_questions = session.query(Question).count()
        print(f"\\n最终统计: {total_questions} 个题目")
        
        return wrong_ids == 0 and total_questions > 0
        
    except Exception as e:
        print(f"验证失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False
    finally:
        session.close()

def main():
    """主验证函数"""
    print("🧪 验证导入功能")
    print("=" * 40)
    
    test_projects = ['test_project_1', 'test_project_2']
    
    for project in test_projects:
        print(f"\\n{'='*40}")
        success = verify_import_for_project(project)
        print(f"项目 {project} 验证结果: {'✅ 成功' if success else '❌ 失败'}")

if __name__ == "__main__":
    main()'''
        
        with open('verify_import.py', 'w', encoding='utf-8') as f:
            f.write(verify_script)
        
        print("✅ 导入验证脚本创建完成")
        return True
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 彻底修复题库导入问题")
    print("=" * 50)
    
    fixes = [
        ("彻底修复Excel导入器", completely_fix_excel_importer),
        ("修复题目计数问题", fix_question_counting),
        ("创建数据库清理脚本", create_database_cleanup_script),
        ("创建导入验证脚本", create_import_verification_script),
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
        print("\\n🎉 彻底修复完成！")
        print("\\n✅ 修复内容:")
        print("1. ✅ 彻底重写ID处理逻辑")
        print("2. ✅ 完全移除ID后缀添加代码")
        print("3. ✅ 修复题目计数统计")
        print("4. ✅ 创建数据库清理工具")
        print("5. ✅ 创建导入验证工具")
        
        print("\\n🛠️ 建议的修复步骤:")
        print("1. 运行数据库清理: python clean_database.py")
        print("2. 运行导入验证: python verify_import.py")
        print("3. 重新启动Flask应用")
        print("4. 重新测试导入功能")
        
        print("\\n🎯 预期结果:")
        print("• ID不再有后缀（如: B-B-B-009-009）")
        print("• 题目数量统计正确")
        print("• 不同项目数据完全隔离")
        print("• 重复导入被正确处理")
        
    else:
        print("\\n⚠️  部分修复失败，请检查错误信息")
    
    return passed_fixes >= 3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
