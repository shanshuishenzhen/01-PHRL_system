#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库表创建脚本
创建组题功能所需的新表
"""

import os
import sys
from sqlalchemy import create_engine, text
from models import Base, Question, Paper, PaperQuestion, QuestionGroup, QuestionBank

def create_tables():
    """创建数据库表"""
    try:
        # 获取数据库路径
        db_path = os.path.join(os.getcwd(), 'local_dev.db')
        
        # 创建数据库引擎
        engine = create_engine(f'sqlite:///{db_path}', echo=True)
        
        print("🔧 开始创建数据库表...")
        print(f"📁 数据库路径: {db_path}")
        
        # 创建所有表
        Base.metadata.create_all(engine)
        
        print("✅ 数据库表创建成功！")
        print("\n📋 已创建的表:")
        print("  - questions (题目表)")
        print("  - papers (试卷表)")
        print("  - paper_questions (试卷题目关联表)")
        print("  - question_groups (题目分组表)")
        print("  - question_banks (题目银行表)")
        
        # 验证表是否创建成功
        with engine.connect() as conn:
            # 检查表是否存在
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            
            print(f"\n🔍 数据库中的表: {', '.join(tables)}")
            
            # 检查各表的记录数
            for table in ['questions', 'papers', 'paper_questions', 'question_groups', 'question_banks']:
                if table in tables:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    row = result.fetchone()
                    count = row[0] if row is not None else 0
                    print(f"  - {table}: {count} 条记录")
        
        print("\n🎉 数据库初始化完成！")
        return True
        
    except Exception as e:
        print(f"❌ 创建数据库表失败: {e}")
        return False

if __name__ == "__main__":
    success = create_tables()
    if success:
        print("\n💡 现在可以启动应用了！")
        print("   运行命令: python app.py")
    else:
        print("\n💡 请检查错误信息并重试")
        sys.exit(1) 