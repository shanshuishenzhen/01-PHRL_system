#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强制清理数据库并重新导入
"""

import sys
import os
sys.path.append('question_bank_web')

from models import Base, Question, QuestionBank
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from excel_importer import import_questions_from_excel

def force_clean_and_reimport():
    """强制清理数据库并重新导入"""
    print("🧹 强制清理数据库并重新导入")
    print("=" * 60)
    
    # 连接到Web应用数据库
    db_path = 'question_bank_web/questions.db'
    engine = create_engine(f'sqlite:///{db_path}')
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 1. 查看当前数据
        question_count = session.query(Question).count()
        bank_count = session.query(QuestionBank).count()
        
        print(f"清理前数据库状态:")
        print(f"  题目数量: {question_count}")
        print(f"  题库数量: {bank_count}")
        
        if question_count > 0:
            # 显示一些示例ID（包括带后缀的）
            sample_questions = session.query(Question).limit(10).all()
            print(f"\n示例题目ID:")
            for q in sample_questions:
                print(f"  {q.id}")
        
        # 2. 强制删除所有数据
        print(f"\n🗑️ 强制删除所有数据...")
        session.execute(text("DELETE FROM questions"))
        session.execute(text("DELETE FROM question_banks"))
        session.commit()
        
        print(f"✅ 数据库强制清理完成")
        
        # 3. 验证清理结果
        question_count = session.query(Question).count()
        bank_count = session.query(QuestionBank).count()
        print(f"清理后数据库状态:")
        print(f"  题目数量: {question_count}")
        print(f"  题库数量: {bank_count}")
        
        # 4. 重新导入样例题库
        print(f"\n📥 重新导入样例题库...")
        excel_file = 'question_bank_web/questions_sample.xlsx'
        
        if os.path.exists(excel_file):
            questions_added, errors = import_questions_from_excel(excel_file, session)
            
            print(f"\n导入结果:")
            print(f"  成功添加: {len(questions_added) if questions_added else 0} 个题目")
            print(f"  错误数量: {len(errors) if errors else 0} 个")
            
            if errors:
                print(f"前5个错误:")
                for i, error in enumerate(errors[:5]):
                    print(f"  {i+1}. {error}")
            
            # 5. 验证导入结果
            final_count = session.query(Question).count()
            final_banks = session.query(QuestionBank).count()
            
            print(f"\n最终数据库状态:")
            print(f"  题目数量: {final_count}")
            print(f"  题库数量: {final_banks}")
            
            # 显示一些示例ID（应该没有后缀）
            if final_count > 0:
                sample_questions = session.query(Question).limit(10).all()
                print(f"\n示例题目ID（应该没有后缀）:")
                for q in sample_questions:
                    print(f"  {q.id}")
                    
                # 检查是否还有带后缀的ID
                bad_ids = session.query(Question).filter(Question.id.like('%_%')).limit(5).all()
                if bad_ids:
                    print(f"\n❌ 仍然发现带后缀的ID:")
                    for q in bad_ids:
                        print(f"  {q.id}")
                else:
                    print(f"\n✅ 所有ID格式正确，没有后缀")
            
        else:
            print(f"❌ 样例题库文件不存在: {excel_file}")
            
    except Exception as e:
        print(f"❌ 操作过程中发生错误: {e}")
        session.rollback()
        import traceback
        print(traceback.format_exc())
    finally:
        session.close()

if __name__ == "__main__":
    force_clean_and_reimport()
    print("\n🎯 强制清理和重新导入完成！请刷新Web页面查看结果。")
