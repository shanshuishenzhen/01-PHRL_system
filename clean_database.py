#!/usr/bin/env python3
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
        print(f"\n{'='*30}")
        clean_project_database(project)

if __name__ == "__main__":
    clean_all_projects()