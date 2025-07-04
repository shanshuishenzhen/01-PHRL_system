#!/usr/bin/env python3
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
        from sqlalchemy import text
        session.execute(text("DELETE FROM questions"))
        session.execute(text("DELETE FROM question_banks"))
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
        
        print(f"\nID格式检查: {correct_ids} 个正确, {wrong_ids} 个错误")
        
        # 4. 统计最终结果
        total_questions = session.query(Question).count()
        print(f"\n最终统计: {total_questions} 个题目")
        
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
        print(f"\n{'='*40}")
        success = verify_import_for_project(project)
        print(f"项目 {project} 验证结果: {'✅ 成功' if success else '❌ 失败'}")

if __name__ == "__main__":
    main()