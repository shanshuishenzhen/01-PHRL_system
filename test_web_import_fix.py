#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Web应用导入修复
"""

import sys
import os
sys.path.append('question_bank_web')

from excel_importer import import_questions_from_excel
from models import Base, Question, QuestionBank
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def test_web_import_fix():
    """测试Web应用的导入修复"""
    print("🧪 测试Web应用导入修复")
    print("=" * 50)
    
    # 创建测试数据库
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("✅ 测试数据库创建成功")
    
    # 测试样例题库文件
    excel_file = 'question_bank_web/questions_sample.xlsx'
    if not os.path.exists(excel_file):
        print(f"❌ 样例题库文件不存在: {excel_file}")
        return False
    
    print(f"✅ 样例题库文件存在: {excel_file}")
    
    try:
        # 第一次导入
        print("\n--- 第一次导入 ---")
        questions_added, errors = import_questions_from_excel(excel_file, session)
        
        print(f"导入结果:")
        print(f"  成功添加: {len(questions_added) if questions_added else 0} 个题目")
        print(f"  错误数量: {len(errors) if errors else 0} 个")
        
        if not questions_added:
            print("❌ 第一次导入失败")
            return False
        
        # 检查ID格式
        print("\n--- 检查ID格式 ---")
        correct_ids = 0
        wrong_ids = 0
        
        for question in questions_added[:10]:  # 检查前10个
            question_id = question['id']
            if '_' in question_id:
                print(f"❌ 错误ID格式: {question_id}")
                wrong_ids += 1
            else:
                print(f"✅ 正确ID格式: {question_id}")
                correct_ids += 1
        
        print(f"\nID格式检查: {correct_ids} 个正确, {wrong_ids} 个错误")
        
        if wrong_ids > 0:
            print("❌ ID格式检查失败")
            return False
        
        # 检查数据库中的实际数据
        print("\n--- 检查数据库数据 ---")
        db_questions = session.query(Question).limit(5).all()
        for q in db_questions:
            if '_' in q.id:
                print(f"❌ 数据库中错误ID: {q.id}")
                return False
            else:
                print(f"✅ 数据库中正确ID: {q.id}")
        
        # 第二次导入（测试重复处理）
        print("\n--- 第二次导入（测试重复处理）---")
        questions_added_2, errors_2 = import_questions_from_excel(excel_file, session)
        
        print(f"第二次导入结果:")
        print(f"  成功添加: {len(questions_added_2) if questions_added_2 else 0} 个题目")
        print(f"  错误数量: {len(errors_2) if errors_2 else 0} 个")
        
        if questions_added_2:
            print("❌ 第二次导入不应该添加新题目（重复检测失败）")
            return False
        
        # 检查总数量
        total_questions = session.query(Question).count()
        print(f"\n数据库中总题目数: {total_questions}")
        
        if total_questions != len(questions_added):
            print(f"❌ 题目数量不匹配: 期望 {len(questions_added)}, 实际 {total_questions}")
            return False
        
        print("✅ 所有测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        print(traceback.format_exc())
        return False
    
    finally:
        session.close()

if __name__ == "__main__":
    success = test_web_import_fix()
    if success:
        print("\n🎉 Web应用导入修复测试成功！")
        print("\n现在可以安全地重新启动Flask应用并测试导入功能。")
    else:
        print("\n❌ Web应用导入修复测试失败！")
    
    sys.exit(0 if success else 1)
