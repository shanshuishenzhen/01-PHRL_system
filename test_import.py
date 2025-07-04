#!/usr/bin/env python3
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
        print(f"\n测试项目: {project_name}")
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
    test_import_with_project()