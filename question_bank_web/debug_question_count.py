#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试题目数量问题
"""

import sqlite3
from models import Question
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def check_database_directly():
    """直接检查数据库"""
    print("=== 直接检查SQLite数据库 ===")
    try:
        conn = sqlite3.connect('questions.db')
        cursor = conn.cursor()
        
        # 查看所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"数据库中的表: {[t[0] for t in tables]}")
        
        if ('questions',) in tables:
            # 查看题型统计
            cursor.execute('SELECT question_type_code, COUNT(*) FROM questions GROUP BY question_type_code ORDER BY question_type_code')
            types = cursor.fetchall()
            print('\n题型统计:')
            total = 0
            for t in types:
                print(f'  题型 {t[0]}: {t[1]} 道题')
                total += t[1]
            print(f'  总计: {total} 道题')
            
            # 检查B型题的具体情况
            cursor.execute("SELECT COUNT(*) FROM questions WHERE question_type_code = 'B'")
            b_count = cursor.fetchone()[0]
            print(f'\nB型题数量: {b_count}')
            
            if b_count > 0:
                cursor.execute("SELECT id FROM questions WHERE question_type_code = 'B' LIMIT 5")
                b_samples = cursor.fetchall()
                print("B型题示例ID:")
                for sample in b_samples:
                    print(f"  {sample[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"直接检查数据库失败: {e}")
        return False

def check_with_sqlalchemy():
    """使用SQLAlchemy检查"""
    print("\n=== 使用SQLAlchemy检查 ===")
    try:
        engine = create_engine('sqlite:///questions.db', echo=False)
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # 检查总题目数
        total_questions = db.query(Question).count()
        print(f"总题目数: {total_questions}")
        
        # 检查各题型数量
        question_types = db.query(Question.question_type_code).distinct().all()
        print("\n题型统计:")
        for qt in question_types:
            if qt[0]:  # 确保不是None
                count = db.query(Question).filter(Question.question_type_code == qt[0]).count()
                print(f"  题型 {qt[0]}: {count} 道题")
        
        # 特别检查B型题
        b_questions = db.query(Question).filter(Question.question_type_code == 'B').all()
        print(f"\nB型题详细信息:")
        print(f"  数量: {len(b_questions)}")
        if b_questions:
            print("  前5个ID:")
            for i, q in enumerate(b_questions[:5]):
                print(f"    {i+1}. {q.id}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"SQLAlchemy检查失败: {e}")
        return False

def test_paper_generation():
    """测试组卷功能"""
    print("\n=== 测试组卷功能 ===")
    try:
        from paper_generator import PaperGenerator
        
        engine = create_engine('sqlite:///questions.db', echo=False)
        Session = sessionmaker(bind=engine)
        db = Session()
        
        generator = PaperGenerator(db)
        
        # 模拟组卷请求
        paper_structure = [
            {
                'question_bank_name': '保卫管理员（三级）理论题库',
                'question_type': 'B',
                'count': 5,
                'score_per_question': 4.0
            }
        ]
        
        knowledge_distribution = {}
        
        print("尝试生成测试试卷...")
        
        # 先检查B型题是否存在
        b_questions = db.query(Question).filter(Question.question_type_code == 'B').all()
        print(f"找到B型题: {len(b_questions)} 道")
        
        if len(b_questions) >= 5:
            paper = generator.generate_paper_by_knowledge_distribution(
                paper_name="测试试卷",
                paper_structure=paper_structure,
                knowledge_distribution=knowledge_distribution
            )
            print(f"✅ 成功生成试卷: {paper.name} (ID: {paper.id})")
        else:
            print(f"❌ B型题数量不足: 需要5道，只有{len(b_questions)}道")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"测试组卷功能失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("题目数量调试工具")
    print("=" * 50)
    
    # 1. 直接检查数据库
    success1 = check_database_directly()
    
    # 2. 使用SQLAlchemy检查
    success2 = check_with_sqlalchemy()
    
    # 3. 测试组卷功能
    success3 = test_paper_generation()
    
    print("\n" + "=" * 50)
    print("调试结果汇总:")
    print(f"  直接数据库检查: {'✅' if success1 else '❌'}")
    print(f"  SQLAlchemy检查: {'✅' if success2 else '❌'}")
    print(f"  组卷功能测试: {'✅' if success3 else '❌'}")

if __name__ == "__main__":
    main()
