#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试Web应用导入问题
"""

import sys
import os
sys.path.append('question_bank_web')

# 直接导入Web应用的模块
from excel_importer import import_questions_from_excel
from models import Base, Question, QuestionBank
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def debug_web_import():
    """调试Web应用导入问题"""
    print("🔍 调试Web应用导入问题")
    print("=" * 60)
    
    # 连接到Web应用数据库
    db_path = 'question_bank_web/questions.db'
    engine = create_engine(f'sqlite:///{db_path}')
    
    # 创建表
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 测试导入
        excel_file = 'question_bank_web/questions_sample.xlsx'
        
        if os.path.exists(excel_file):
            print(f"📥 测试导入样例题库: {excel_file}")
            
            # 第一次导入
            questions_added, errors = import_questions_from_excel(excel_file, session)
            
            print(f"\n导入结果:")
            print(f"  成功添加: {len(questions_added) if questions_added else 0} 个题目")
            print(f"  错误数量: {len(errors) if errors else 0} 个")
            
            if errors:
                print(f"前3个错误:")
                for i, error in enumerate(errors[:3]):
                    print(f"  {i+1}. {error}")
            
            # 检查数据库中的实际数据
            print(f"\n📊 数据库状态:")
            question_count = session.query(Question).count()
            bank_count = session.query(QuestionBank).count()
            
            print(f"  题目数量: {question_count}")
            print(f"  题库数量: {bank_count}")
            
            # 显示前10个题目ID
            if question_count > 0:
                sample_questions = session.query(Question).limit(10).all()
                print(f"\n前10个题目ID:")
                for i, q in enumerate(sample_questions, 1):
                    print(f"  {i}. {q.id}")
                    
                # 检查是否有带后缀的ID
                bad_questions = session.query(Question).filter(
                    Question.id.like('%_保卫管理%') | 
                    Question.id.like('%_视频创推%')
                ).limit(5).all()
                
                if bad_questions:
                    print(f"\n❌ 发现带后缀的ID:")
                    for q in bad_questions:
                        print(f"  {q.id}")
                else:
                    print(f"\n✅ 没有发现带后缀的ID")
            
        else:
            print(f"❌ 样例题库文件不存在: {excel_file}")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        print(traceback.format_exc())
    finally:
        session.close()

if __name__ == "__main__":
    debug_web_import()
    print("\n🎯 调试完成！")
