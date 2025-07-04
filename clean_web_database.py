#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理Web应用数据库
"""

import sys
import os
sys.path.append('question_bank_web')

from models import Base, Question, QuestionBank
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def clean_web_database():
    """清理Web应用数据库"""
    print("🧹 清理Web应用数据库")
    print("=" * 50)
    
    # 连接到Web应用数据库
    db_path = 'question_bank_web/questions.db'
    engine = create_engine(f'sqlite:///{db_path}')
    
    # 检查数据库是否存在
    if os.path.exists(db_path):
        print(f"✅ 找到数据库文件: {db_path}")
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # 查看当前数据
            question_count = session.query(Question).count()
            bank_count = session.query(QuestionBank).count()
            
            print(f"当前数据库状态:")
            print(f"  题目数量: {question_count}")
            print(f"  题库数量: {bank_count}")
            
            if question_count > 0:
                # 显示一些示例ID
                sample_questions = session.query(Question).limit(5).all()
                print(f"\n示例题目ID:")
                for q in sample_questions:
                    print(f"  {q.id}")
            
            # 清理所有数据
            print(f"\n🗑️ 清理所有数据...")
            session.query(Question).delete()
            session.query(QuestionBank).delete()
            session.commit()
            
            print(f"✅ 数据库清理完成")
            
            # 验证清理结果
            question_count = session.query(Question).count()
            bank_count = session.query(QuestionBank).count()
            print(f"清理后数据库状态:")
            print(f"  题目数量: {question_count}")
            print(f"  题库数量: {bank_count}")
            
        except Exception as e:
            print(f"❌ 清理过程中发生错误: {e}")
            session.rollback()
        finally:
            session.close()
    else:
        print(f"⚠️ 数据库文件不存在: {db_path}")
        print("将在首次运行时自动创建")

if __name__ == "__main__":
    clean_web_database()
    print("\n🎯 数据库清理完成！现在可以重新启动Flask应用并导入数据。")
