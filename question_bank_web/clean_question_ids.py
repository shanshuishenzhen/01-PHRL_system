#!/usr/bin/env python3
"""
清理题目ID中的多余后缀
将形如 "B-A-A-A-001-001#df2937a4-5cb1-467f-a760-4d3c35aa77d8" 的ID
清理为 "B-A-A-A-001-001"
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Question, QuestionBank

def clean_question_ids():
    """清理题目ID中的多余后缀 - 使用删除重复数据的策略"""

    # 数据库配置
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///questions.db')
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # 查找所有包含#的题目ID
        questions_with_suffix = db.query(Question).filter(Question.id.like('%#%')).all()

        print(f"找到 {len(questions_with_suffix)} 个包含后缀的题目ID")

        if not questions_with_suffix:
            print("没有需要清理的题目ID")
            return

        # 按题库分组，找出重复的原始ID
        from collections import defaultdict
        bank_questions = defaultdict(list)

        for question in questions_with_suffix:
            original_id = question.id.split('#')[0]
            bank_id = question.question_bank_id
            bank_questions[(bank_id, original_id)].append(question)

        # 统计重复情况
        duplicates_to_remove = []
        questions_to_update = []

        for (bank_id, original_id), questions in bank_questions.items():
            if len(questions) > 1:
                # 有重复，保留第一个，删除其他的
                print(f"发现重复ID {original_id} 在题库 {bank_id} 中有 {len(questions)} 个")
                questions_to_update.append(questions[0])  # 保留第一个
                duplicates_to_remove.extend(questions[1:])  # 删除其他的
            else:
                # 没有重复，直接更新
                questions_to_update.append(questions[0])

        print(f"将删除 {len(duplicates_to_remove)} 个重复题目")
        print(f"将更新 {len(questions_to_update)} 个题目ID")

        if duplicates_to_remove:
            response = input(f"确认删除 {len(duplicates_to_remove)} 个重复题目？(y/N): ")
            if response.lower() != 'y':
                print("清理操作已取消")
                return

        # 删除重复的题目
        for question in duplicates_to_remove:
            print(f"删除重复题目: {question.id}")
            db.delete(question)

        # 更新剩余题目的ID
        for question in questions_to_update:
            old_id = question.id
            new_id = old_id.split('#')[0]
            question.id = new_id
            print(f"更新: {old_id} -> {new_id}")

        # 提交更改
        db.commit()
        print(f"成功删除了 {len(duplicates_to_remove)} 个重复题目")
        print(f"成功更新了 {len(questions_to_update)} 个题目ID")

    except Exception as e:
        db.rollback()
        print(f"清理过程中发生错误: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    clean_question_ids()
